#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import argparse
from pathlib import Path
from Dmux import utils

main_parser = argparse.ArgumentParser(prog='dmux')
sub_parser = main_parser.add_subparsers(help='sub-command help')
parser_run = sub_parser.add_parser('run', help='run subcommand help')
parser_logs = sub_parser.add_parser('logs', help='logs subcommand help')


def run(args):
    runs = utils.get_run_directories(args.rundir, seq_dir=args.seq_dir)
    config = utils.base_config()
 
    for (rundir, run_infos) in runs:
        sample_sheet = run_infos['samplesheet']
        config['runs'].append(rundir)
        config['run_ids'].append(rundir.name)
        config['projects'].append(list(set([_sample.Sample_Project for _sample in sample_sheet.samples])))
        pairs = ['1', '2'] if sample_sheet.is_paired_end else ['1']
        config['reads_out'].append(
            [f'{_sample.Sample_ID}_S{str(i)}_R{pair}_001.fastq.gz' \
             for i, _sample in enumerate(sample_sheet.samples, start=1) for pair in pairs]
        )
        config['rnums'].append(pairs)
        config['bcl_files'].append(list(Path(rundir).rglob('*.bcl.*')))
        out_to = Path(args.output, f"{sample_sheet.Header['Experiment Name']}_demux") if args.output \
            else Path(rundir, f"{sample_sheet.Header['Experiment Name']}_demux")
        utils.valid_run_output(out_to, dry_run=args.pretend)
        config['out_to'].append(out_to)

    utils.exec_demux_pipeline(config, dry_run=args.pretend)


def ngs_qc(args):
    # kraken, kiaju, fastp, fastqscreen, fastqc, multiqc
    pass


def logs(args):
    # 1. check if sqlite log exists, make if not exists, return empty log message
    # 2. given it exists, query log based on cli filters
    # 3. return log pretty message
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(prog='dmux')
    sub_parsers = main_parser.add_subparsers(help='run subcommand help')

    parser_run = sub_parsers.add_parser('run')
    parser_run.add_argument('rundir', metavar='<run directory>', nargs="+", type=utils.valid_run_input, 
                            help='Full & complete run id (format YYMMDD_INSTRUMENTID_TIME_FLOWCELLID) or absolute paths')
    parser_run.add_argument('-s', '--seq_dir', metavar='<sequencing directory', default=None, type=str,
                            help='Root directory for sequencing data (defaults for biowulf/bigsky/locus), must contain directories ' + \
                            'matching run ids, if not using full paths.')
    parser_run.add_argument('-o', '--output', metavar='<output directory>', default=None, type=str, 
                            help='Top-level output directory for demultiplexing data (defaults to input directory + runid + "_demux")')
    parser_run.add_argument('-p', '--pretend', action='store_true', 
                            help='Dry run the demultiplexing workflow')
    # add non-default samplesheet names
    # add in flag for running disabling qc
    parser_run.set_defaults(func = run)

    parser_logs = sub_parsers.add_parser('logs', help='logs subcommand help')
    parser_logs.add_argument('Run', type=utils.valid_runid, 
                             help='Partial or full run id, can use wildcards')
    parser_logs.add_argument('--before', type=str, dest='before', default=None, required=False, 
                             help='Only look at log results demultiplexed before this date (format MMDDYYYY)')
    parser_logs.add_argument('--after', type=str, dest='after', default=None,  required=False, 
                             help='Only look at log results demultiplexed after this date (format MMDDYYYY)')
    parser_logs.set_defaults(func = logs)

    args = main_parser.parse_args()
    args.func(args)