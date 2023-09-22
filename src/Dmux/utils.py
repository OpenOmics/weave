#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   misc. helper functions for the Dmux software package
# ~~~~~~~~~~~~~~~
import re
from argparse import ArgumentTypeError
from Dmux.config import DIRECTORY_CONFIGS
from dateutil.parser import parse as date_parser
from pathlib import Path
from socket import gethostname


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


def get_current_server():
    hn = gethostname()
    # bigsky hostnames
    re_bigsky = (r"ai-rml.*\.niaid\.nih\.gov", 'bigsky')

    # biowulf hostnames
    re_biowulf_head = (r"biowulf\.nih\.gov", 'biowulf')
    re_biowulf_compute = (r"cn\d{4}", 'biowulf')
    
    # locus hostnames
    re_locus_head = (r"ai\-submit\d{1}", 'locus')
    re_locus_compute = (r"ai\-hpcn\d{3}", 'locus')

    host_profiles = [re_bigsky, re_biowulf_compute, re_biowulf_head, re_locus_compute, re_locus_head]

    host = None
    for pat, this_host in host_profiles:
        if re.match(pat, hn):
            host = this_host
            break
    if host is None:
        raise ValueError(f'Unknown host profile')
    return host


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
    host = get_current_server()
    seq_dirs = DIRECTORY_CONFIGS[host]['seq']

    valid_run = None
    if Path(run).exists():
        # this is a fill pathrun directory
        valid_run = Path(run).resolve()
    elif run in list(map(lambda d: d.name, seq_dirs)):
        for _r in seq_dirs:
            if run == _r.name:
                valid_run = _r.resolve()
    else:
        raise ArgumentTypeError(f'Sequencing run {esc_colors.BOLD}"{run}"{esc_colors.ENDC} does not exist on server {esc_colors.BOLD}"{host}"{esc_colors.ENDC}')
        
    return valid_run