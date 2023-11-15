#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   Miscellaneous utility functions for the Dmux software package
# ~~~~~~~~~~~~~~~
import re
import json
import os
import yaml
import sys
from argparse import ArgumentTypeError
from dateutil.parser import parse as date_parser
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path, PurePath

# ~~~ internals ~~~
from .files import parse_samplesheet, mk_or_pass_dirs
from .config import SNAKEFILE, DIRECTORY_CONFIGS, get_current_server, get_resource_config


host = get_current_server()


class esc_colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PathJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PurePath):
            return str(obj)
        return super(self).default(obj)


def valid_runid(id_to_check):
    '''
        Given an input ID get it's validity against the run id format:
            YYMMDD_INSTRUMENTID_TIME_FLOWCELLID
    '''
    id_to_check = str(id_to_check)
    id_parts = id_to_check.split('_')
    if len(id_parts) != 4:
        raise ValueError(f"Invalid run id format: {id_to_check}")
    try:
        # YY MM DD
        date_parser(id_parts[0])
    except Exception as e:
        raise ValueError('Invalid run id date') from e
    try:
        # HH MM
        h = int(id_parts[2][0:3])
        m = int(id_parts[2][2:])
    except ValueError as e:
        raise ValueError('Invalid run id time') from e

    if h >= 25 or m >= 60:
        raise ValueError('Invalid run id time: ' + h + m)

    # TODO: check instruments against labkey
    return id_to_check


def valid_run_input(run):
    regex_run_id = r"(\d{6})_([A-Z]{2}\d{6})_(\d{4})_([A-Z0-9]{10})"
    match_id = re.search(regex_run_id, run, re.MULTILINE)
    if match_id:
        return run

    if Path(run).exists():
        run = Path(run).absolute()
        return run

    raise ArgumentTypeError("Invalid run value, neither an id or existing path: " + str(run))


def exec_snakemake(popen_cmd, local=False, dry_run=False, env=None, cwd=None):
    # async execution w/ filter: 
    #   - https://gist.github.com/DGrady/b713db14a27be0e4e8b2ffc351051c7c
    #   - https://lysator.liu.se/~bellman/download/asyncproc.py
    #   - https://gist.github.com/kalebo/1e085ee36de45ffded7e5d9f857265d0
    if env is None: env = {}

    popen_kwargs = dict()
    if env:
        popen_kwargs['env'] = env
    else:
        popen_kwargs['env'] = {}

    if cwd:
        popen_kwargs['cwd'] = cwd
    else:
        popen_kwargs['cwd'] = str(Path.cwd())

    if local or dry_run:
        proc = Popen(popen_cmd, stdout=PIPE, stderr=STDOUT, **popen_kwargs)
        parent_jobid = None
        for line in proc.stdout:
            lutf8 = line.decode('utf-8')
            jid_search = re.search(r"external jobid \'(\d+)\'", lutf8, re.MULTILINE)
            if jid_search:
                parent_jobid = int(jid_search.group(1))
            sys.stdout.write(lutf8)
        snakemake_run_out, _ = proc.communicate()
    else:
        jobscript = mk_sbatch_script(cwd, ' '.join([str(x) for x in popen_cmd]))
        proc = Popen(['sbatch', jobscript], stdout=PIPE, stderr=STDOUT, **popen_kwargs)
        snakemake_run_out, _ = proc.communicate()
        jid_search = re.search(r"(\d{5,10})", snakemake_run_out.decode('utf-8'), re.MULTILINE)
        if jid_search:
            parent_jobid = jid_search.group(1)
    mode = "local" if local or dry_run else "headless"
    if parent_jobid:
        print(f"{esc_colors.OKGREEN}> {esc_colors.ENDC} Master job submitted in '{mode}' mode on job {esc_colors.OKGREEN}{str(parent_jobid)}{esc_colors.ENDC}")
    return proc.returncode == 0, parent_jobid


def mk_sbatch_script(wd, cmd):
    master_job_script = \
    """
    #!/bin/bash
    #SBATCH --job-name=dmux_master
    #SBATCH --output=./slurm/masterjob_snakemake_%j.out
    #SBATCH --error=./slurm/masterjob_snakemake_%j.err
    #SBATCH --ntasks=1
    #SBATCH --cpus-per-task=2
    #SBATCH --time=02-00:00:00
    #SBATCH --export=ALL
    #SBATCH --mem=16g
    """.lstrip()
    master_job_script += get_mods(init=True) + "\n"
    master_job_script += cmd
    master_job_script = '\n'.join([x.lstrip() for x in master_job_script.split('\n')])
    master_script_location = Path(wd, 'slurm', 'master_jobscript.sh').absolute()
    master_script_location.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    with open(master_script_location, 'w') as fo:
        fo.write(master_job_script)
    return master_script_location


def get_mods(init=False):
    mods_needed = ['snakemake', 'singularity']
    mod_cmd = []

    if host == 'bigsky':
        mod_cmd.append('source /gs1/apps/user/rmlspack/share/spack/setup-env.sh')
        mod_cmd.append('spack load miniconda3@4.11.0')
        mod_cmd.append('source activate snakemake7-19-1')
    else:
        if init:
            mod_cmd.append('source /etc/profile.d/modules.sh')
        else:
            mod_cmd.append('module purge')
        mod_cmd.append(f"module load {' '.join(mods_needed)}")

    return '; '.join(mod_cmd)


def get_mounts(*extras):
    mount_binds = []
    resources = get_resource_config()

    if resources:
        for this_mount_label, this_mount_attrs in resources['mounts'].items():
            this_mount_signature = this_mount_attrs['from'] + ':' + this_mount_attrs['to'] + ':' + this_mount_attrs['mode']
            mount_binds.append(this_mount_signature)

    if extras:
        for extra in extras:
            if not Path(extra).exists():
                raise FileNotFoundError(f"Can't mount {str(extra)}, it doesn't exist!")
        mount_binds.extend(extras)

    mounts = []
    for bind in mount_binds:
        if ':' in str(bind):
            bind = str(bind)
            bind = bind.split(':')
            if len(bind) >= 2:
                file_from = str(Path(bind[0]).resolve())
                file_to = str(Path(bind[1]).absolute())

            mode = str(bind[2]) if len(bind) >= 3 else 'rw'

            if mode not in ('ro', 'rw'):
                mode = 'rw'
        else:
            if not Path(bind).exists():
                raise FileNotFoundError(f"Can't mount {str(bind)}, it doesn't exist!")
            file_to, file_from, mode = str(bind), str(bind), 'rw'
        mounts.append(file_from + ':' + file_to + ':' + mode)

    return "\'-B " + ','.join(mounts) + "\'"


def ensure_pe_adapters(samplesheets):
    pe = []
    for ss in samplesheets:
        this_is_pe = [ss.is_paired_end]
        for this_sample in ss.samples:
            this_is_pe.append(str(this_sample.index) not in ('', None, 'nan'))
            this_is_pe.append(str(this_sample.index2) not in ('', None, 'nan'))
        pe.extend(this_is_pe)
    return all(pe)


def exec_pipeline(configs, dry_run=False, local=False):
    this_instrument = 'Illumnia'
    snake_file = SNAKEFILE[this_instrument]['ngs_qc']
    fastq_demux_profile = DIRECTORY_CONFIGS[get_current_server()]['profile']
    profile_config = {}
    if Path(fastq_demux_profile, 'config.yaml').exists():
        profile_config.update(yaml.safe_load(open(Path(fastq_demux_profile, 'config.yaml'))))

    top_singularity_dirs = [Path(c_dir, '.singularity').absolute() for c_dir in configs['out_to']]
    top_config_dirs = [Path(c_dir, '.config').absolute() for c_dir in configs['out_to']]
    _dirs = top_singularity_dirs + top_config_dirs
    mk_or_pass_dirs(*_dirs)
    skip_config_keys = ('resources', 'runqc')

    for i in range(0, len(configs['run_ids'])):
        this_config = {k: (v[i] if k not in skip_config_keys else v) for k, v in configs.items() if v}
        this_config.update(profile_config)
        extra_to_mount = [this_config['out_to'], this_config['demux_input_dir']]
        singularity_binds = get_mounts(*extra_to_mount)
        config_file = Path(this_config['out_to'], '.config', f'config_job_{str(i)}.json').absolute()
        json.dump(this_config, open(config_file, 'w'), cls=PathJSONEncoder, indent=4)
        top_env = {}
        top_env['PATH'] = os.environ["PATH"]
        top_env['SNK_CONFIG'] = str(config_file.absolute())
        # top_env['LOAD_MODULES'] = get_mods()
        top_env['SINGULARITY_CACHEDIR'] = str(Path(this_config['out_to'], '.singularity').absolute())
        this_cmd = [
            "snakemake",
            "-pr",
            "--use-singularity",
            "--rerun-incomplete",
            "--rerun-triggers", "mtime",
            "--verbose",
            "-s", snake_file,
            "--profile", fastq_demux_profile
        ]
        if singularity_binds:
            this_cmd.extend(["--singularity-args", singularity_binds])

        if not local:
            this_cmd.extend(["--profile", f"{fastq_demux_profile}"])

        if dry_run:
            print(f"{esc_colors.OKGREEN}> {esc_colors.ENDC}{esc_colors.UNDERLINE}Dry run{esc_colors.ENDC} " + \
                  f"demultiplexing of run {esc_colors.BOLD}{esc_colors.OKGREEN}{this_config['run_ids']}{esc_colors.ENDC}...")
            this_cmd.extend(['--dry-run', '-p'])
        else:
            print(f"{esc_colors.OKGREEN}> {esc_colors.ENDC}Executing ngs qc pipeline for run {esc_colors.BOLD}"
                  f"{esc_colors.OKGREEN}{this_config['run_ids']}{esc_colors.ENDC}...")

        print(' '.join(map(str, this_cmd)))
        exec_snakemake(this_cmd, local=local, dry_run=dry_run, env=top_env, cwd=str(Path(this_config['out_to']).absolute()))

