#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   file system helper functions for the Dmux software package
# ~~~~~~~~~~~~~~~
from pathlib import Path
import xml.etree.ElementTree as ET
from os import access as check_access, R_OK, W_OK
from functools import partial
from .samplesheet import IllumniaSampleSheet
from .config import get_current_server, LABKEY_CONFIGS, DIRECTORY_CONFIGS


def get_all_seq_dirs(top_dir, server):
    """
        Gather and return all sequencing directories from the `top_dir`. 
        This is tightly coupled at the moment to the directory that is on RML-BigSky.
        In the future will need to the take a look at how to do this more generally
    """
    if isinstance(top_dir, str): top_dir = Path(top_dir)
    _dirs = []
    for _file in top_dir.glob('*'):
        if _file.is_dir():
            for _file2 in _file.glob('*'):
                if _file2.is_dir() and check_access(_file2, R_OK):
                    _dirs.append(_file2.resolve())
    # check if directory is processed or not
    return _dirs


def valid_run_output(output_directory, dry_run=False):
    if dry_run:
        return Path(output_directory).absolute()
    output_directory = Path(output_directory).absolute()
    if not output_directory.exists():
        output_directory.mkdir(parents=True, mode=0o765)
    
    if not check_access(output_directory, W_OK):
        raise PermissionError(f'Can not write to output directory {output_directory}')
    return output_directory


def get_all_staged_dirs(top_dir, server):
    return list(filter(partial(is_dir_staged, server), get_all_seq_dirs(top_dir, server)))


def runid2samplesheet(runid, top_dir=DIRECTORY_CONFIGS['bigsky']['seq']):
    """
        Given a valid run id return the path to the sample sheet
    """
    ss_path = Path(top_dir, runid)
    if not ss_path.exists():
        raise FileNotFoundError(f"Run directory does not exist: {ss_path}")
    if Path(ss_path, f"SampleSheet_{runid}.txt").exists():
        ss_path = Path(ss_path, f"SampleSheet_{runid}.txt")
    elif Path(ss_path, f"SampleSheet_{runid}.csv").exists():
        ss_path = Path(ss_path, f"SampleSheet_{runid}.csv")
    else:
        raise FileNotFoundError("Run sample sheet does not exist: " + str(ss_path) + f"/SampleSheet_{runid}.[txt, csv]")
    return ss_path


def mk_or_pass_dirs(*dirs):
    for _dir in dirs:
        if isinstance(_dir, str):
            _dir = Path(_dir)
        _dir = _dir.resolve()
        _dir.mkdir(mode=0o755, parents=True, exist_ok=True)
    return True


def sniff_samplesheet(ss):
    """
        Given a sample sheet file return the appropriate function to parse the
        sheet.
    """
    return IllumniaSampleSheet


def parse_samplesheet(ss):
    """
        Parse the sample sheet into data structure
    """
    parser = sniff_samplesheet(ss)
    return parser(ss)


def is_dir_staged(server, run_dir):
    """
        filter check for wheter or not a directory has the appropriate breadcrumbs or not

        RTAComplete.txt - file transfer from instrument breadcrumb, CSV file with values:
            Run Date, Run time, Instrument ID        
    """
    analyzed_checks = [
        Path(run_dir, 'RTAComplete.txt').exists(),
        Path(run_dir, 'SampleSheet.csv').exists(),
        Path(run_dir, 'RunInfo.xml').exists(),
    ]
    return all(analyzed_checks)


def find_demux_dir(run_dir):
    demux_stat_files = [x for x in Path(run_dir).rglob('DemultiplexingStats.xml')]

    if len(demux_stat_files) != 1:
        raise FileNotFoundError
    
    return Path(demux_stat_files[0], '..').absolute()


def get_run_directories(runids, seq_dir=None):
    host = get_current_server()
    seq_dirs = Path(seq_dir).absolute() if seq_dir else Path(DIRECTORY_CONFIGS[host]['seqroot'])
    seq_contents = [_child for _child in seq_dirs.iterdir()]
    seq_contents_names = [child for child in map(lambda d: d.name, seq_contents)]
    
    run_paths, invalid_runs  = [], []
    run_return = []
    for run in runids:
        if Path(run).exists():
            # this is a full pathrun directory
            run_paths.append(Path(run))
        elif run in seq_contents_names:
            for _r in seq_contents:
                if run == _r.name:
                    run_paths.append(_r)
        else:
            invalid_runs.append(run)

    for run_p in run_paths:
        rid = run_p.name
        this_run_info = dict(run_id=rid)
        if Path(run_p, 'SampleSheet.csv').exists():
            this_run_info['samplesheet'] = parse_samplesheet(Path(run_p, 'SampleSheet.csv').absolute())
        else:
            raise FileNotFoundError(f'Run {rid}({run_p}) does not have a sample sheet.')
        if Path(run_p, 'RunInfo.xml').exists():
            run_xml = ET.parse(Path(run_p, 'RunInfo.xml').absolute()).getroot()
            this_run_info.update({info.tag: info.text for run in run_xml for info in run \
                             if info.text is not None and info.text.strip() not in ('\n', '')})
        else:
            raise FileNotFoundError(f'Run {rid}({run_p}) does not have a RunInfo.xml file.')
        run_return.append((run_p, this_run_info))

    if invalid_runs:
        raise ValueError('Runs entered are invalid (missing sequencing artifacts or directory does not exist): \n' + \
                         ', '.join(invalid_runs))
    
    return run_return