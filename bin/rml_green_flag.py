#!/usr/bin/env python
import argparse
import sqlite3
import sys
from pathlib import Path
from Dmux.config import DIRECTORY_CONFIGS
from Dmux.files import runid2samplesheet, parse_samplesheet
from Dmux.utils import valid_runid


SERVER_NAME = 'bigsky'
# production directory
# SEQUENCING_DIR = DIRECTORY_CONFIGS[SERVER_NAME]['seq']
# development directory
SEQUENCING_DIR = Path('/gs1/Scratch/test_bcl2fastq/')


def demux(args):
    sample_sheet = parse_samplesheet(runid2samplesheet(args.RunID, top_dir=SEQUENCING_DIR))
    # 1. form sample sheet into snakemake configuration json
    # 2. subprocess.Popen to kick off valid demux snakemake pipeline
    # 3. Log demultiplexing pipeline execution, run time, start finish, 
    import ipdb; ipdb.set_trace()


def logs(args):
    # 1. check if sqlite log exists, make if not exists, return empty log message
    # 2. given it exists, query log based on cli filters
    # 3. return log pretty message
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(prog='rml_green_flag')
    sub_parsers = main_parser.add_subparsers(help='run subcommand help')

    parser_demux = sub_parsers.add_parser('demux')
    parser_demux.add_argument('RunID', type=valid_runid, help='Full & complete run id, no wildcards or regex (format YYMMDD_INSTRUMENTID_TIME_FLOWCELLID)')
    parser_demux.set_defaults(func = demux)

    parser_logs = sub_parsers.add_parser('logs', help='logs subcommand help')
    parser_logs.add_argument('Run', type=valid_runid, help='Partial or full run id, can use wildcards')
    parser_logs.add_argument('--before', type=str, dest='before', default=None, required=False, help='Only look at log results demultiplexed before this date (format MMDDYYYY)')
    parser_logs.add_argument('--after', type=str, dest='after', default=None,  required=False, help='Only look at log results demultiplexed after this date (format MMDDYYYY)')
    parser_logs.set_defaults(func = logs)

    args = main_parser.parse_args()
    args.func(args)