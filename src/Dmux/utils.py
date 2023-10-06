#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   misc. helper functions for the Dmux software package
# ~~~~~~~~~~~~~~~
import re
import json
import os
import yaml
import sys
import time
import xml.etree.ElementTree as ET
from Dmux.files import parse_samplesheet
from threading import Thread
from os import access as check_access, W_OK
from argparse import ArgumentTypeError
from Dmux.config import DIRECTORY_CONFIGS, SNAKEFILE, get_current_server
from Dmux.modules import get_demux_mods, init_demux_mods, close_demux_mods
from dateutil.parser import parse as date_parser
from subprocess import Popen, PIPE
from tempfile import TemporaryDirectory
from pathlib import Path, PurePath


DEFAULT_CONFIG_KEYS = ('runs', 'run_ids', 'projects', 'reads_out', 'out_to', 'rnums', 'bcl_files')


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


def month2fiscalq(month):
    if month < 1 or month > 12:
        return None
    return 'Q' + str(int((month/4)+1))


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
    regex_run_id = r"(\d{6})_([A-Z]{2}\d{6})_(\d{4})_([A-Z]{10})"
    match_id = re.search(regex_run_id, run, re.MULTILINE)
    if match_id:
        return run
    
    if Path(run).exists():
        run = Path(run).resolve()
        return run
    
    raise ArgumentTypeError("Invalid run value, neither an id or existing path: " + str(run)) 


def get_run_directories(runids, seq_dir=None):
    host = get_current_server()
    seq_dirs = Path(seq_dir).resolve() if seq_dir else DIRECTORY_CONFIGS[host]['seq'] 
    
    run_paths, invalid_runs  = [], []
    run_return = []
    for run in runids:
        if Path(run).exists():
            # this is a full pathrun directory
            run_paths.append(Path(run).resolve())
        elif run in list(map(lambda d: d.name, seq_dirs)):
            for _r in seq_dirs:
                if run == _r.name:
                    run_paths.append(_r.resolve())
        else:
            invalid_runs.append(run)

    for run_p in run_paths:
        rid = run_p.name
        this_run_info = {}
        if Path(run_p, 'SampleSheet.csv').exists():
            this_run_info['samplesheet'] = parse_samplesheet(Path(run_p, 'SampleSheet.csv').resolve())
        else:
            raise FileNotFoundError(f'Run {rid}({run_p}) does not have a sample sheet.')
        if Path(run_p, 'RunInfo.xml').exists():
            run_xml = ET.parse(Path(run_p, 'RunInfo.xml').resolve()).getroot()
            this_run_info.update({info.tag: info.text for run in run_xml for info in run \
                             if info.text is not None and info.text.strip() not in ('\n', '')})
        else:
            raise FileNotFoundError(f'Run {rid}({run_p}) does not have a RunInfo.xml file.')
        run_return.append((run_p, this_run_info))

    if invalid_runs:
        raise ValueError('Runs entered are invalid (missing sequencing artifacts or directory does not exist): \n' + \
                         ', '.join(invalid_runs))
    
    return run_return


def valid_run_output(output_directory, dry_run=False):
    if dry_run:
        return Path(output_directory).resolve()
    output_directory = Path(output_directory).resolve()
    if not output_directory.exists():
        output_directory.mkdir(parents=True, mode=0o765)
    else:
        raise FileExistsError(f'Output directory, {output_directory} exists already. Select alternative or delete existing.')
    if not check_access(output_directory, W_OK):
        raise PermissionError(f'Can not write to output directory {output_directory}')
    return output_directory


def exec_snakemake(popen_cmd, env=None):
    if env is None: env = {}

    proc = Popen(popen_cmd, stderr=PIPE, env=env)
    _c = 0
    while True:
        output = proc.stderr.readline()
        _poll = proc.poll()

        time.sleep(0.5) 
        
        if output:
            this_output = output.strip().decode('utf-8')
            jid_re = r"Submitted job (\d{1,}) with external jobid '(\d{7,})'"
            out_find = re.search(jid_re, this_output)
            if out_find is not None:
                internal_jid, external_jid = out_find.groups()
                job_msg = f"\t- {esc_colors.OKGREEN}Snakemake{esc_colors.ENDC} job id: {internal_jid}, {esc_colors.OKGREEN}slurm{esc_colors.ENDC} job id: {external_jid}"
                print(job_msg)
                break
        if _poll is not None:
            if _poll == 1:
                raise ChildProcessError(esc_colors.FAIL + 'Snakemake execution error: \n\n' + output.decode('utf-8') + esc_colors.ENDC)
            if _poll == 0:
                _c += 1
                if _c > 2: continue
                break
    return True


def exec_demux_pipeline(configs, dry_run=False, local=False):
    init_mods = init_demux_mods()
    assert init_mods, f"Failed to initialize modules: {get_demux_mods()}"
    # TODO: when or if other instrument profiles are needed, 
    #       we will need to expand this portion to 
    #       determine instrument type/brand by some method.
    this_instrument = 'Illumnia'
    snake_file = SNAKEFILE[this_instrument + '_demux']
    fastq_demux_profile = DIRECTORY_CONFIGS[get_current_server()]['profile']
    profile_config = {}
    if Path(fastq_demux_profile, 'config.yaml').exists():
        profile_config.update(yaml.safe_load(open(Path(fastq_demux_profile, 'config.yaml'))))

    top_output_dir = Path(configs['out_to'][0], '..', '.singularity').resolve()
    top_config_dir = Path(configs['out_to'][0], '..', '.config').resolve()
    if not top_output_dir.exists():
        top_output_dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    if not top_config_dir.exists():
        top_config_dir.mkdir(mode=0o755, parents=True, exist_ok=True)

    for i in range(0, len(configs['projects'])):
        this_config = {k: v[i] for k, v in configs.items()}
        this_config.update(profile_config)
        config_file = Path(top_config_dir, f'config_job_{str(i)}.json').resolve()
        json.dump(this_config, open(config_file, 'w'), cls=PathJSONEncoder, indent=4)
        top_env = os.environ.copy()
        top_env['SNK_CONFIG'] = str(config_file.resolve())
        top_env['LOAD_MODULES'] = get_demux_mods()
        top_env['SINGULARITY_CACHEDIR'] = str(Path(top_output_dir, '.singularity'))
        this_cmd = [
            "snakemake", "--use-singularity", "--singularity-args", \
            f"\"-B {this_config['runs']},{str(this_config['out_to'])}\"", \
            "-s", f"{snake_file}", 
        ]

        if not local:
            this_cmd.extend(["--profile", f"{fastq_demux_profile}"])

        if dry_run:
            print(f"{esc_colors.OKGREEN}> {esc_colors.ENDC} {esc_colors.UNDERLINE}Dry run{esc_colors.ENDC} demultiplexing of run {esc_colors.BOLD}{esc_colors.OKGREEN}{this_config['run_ids']}{esc_colors.ENDC}...")
            time.sleep(0.5)
            this_cmd.extend(['--dry-run', '-p'])
            proc = Popen(this_cmd, env=top_env)
            proc.communicate()
        else:
            print(f"{esc_colors.OKGREEN}> {esc_colors.ENDC}Executing demultiplexing of run{esc_colors.BOLD} {esc_colors.OKGREEN}{this_config['run_ids']}{esc_colors.ENDC}...")
            exec_snakemake(this_cmd, top_env)
               
        
    close_demux_mods()


def exec_ngs_qc_pipeline():
    singularity_binds = "-B " + \
        "/data/OpenOmics/references/Dmux/kraken2/k2_pluspfp_20230605:/mnt/kraken2:rw," + \
        "/gpfs/gsfs8/users/OpenOmics/references/Dmux/kaiju/kaiju_db_nr_euk_2023-05-10:/mnt/kaiju:rw"



def base_config():
    this_config = {}
    for elem_key in DEFAULT_CONFIG_KEYS:
        this_config[elem_key] = []
    return this_config