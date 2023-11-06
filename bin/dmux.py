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
    # 1. form sample sheet into snakemake configuration json ✓
    # 2. subprocess.Popen to kick off valid demux snakemake pipeline ✓
    # 3. Log demultiplexing pipeline execution, run time, start finish 
    # 4. Allow for non-default samplesheet names
    # 5. Allow for flag to disable qc
    runs = utils.get_run_directories(args.rundir, seq_dir=args.seq_dir)
    config = utils.base_run_config()
 
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
        utils.valid_run_output(out_to, dry_run=args.dry_run)
        config['out_to'].append(out_to)

    utils.exec_demux_pipeline(config, dry_run=args.dry_run, local=args.local)

    # if qc not disabled:
    #   - mutate config into structs/data appropriate for `args`
    #   ngsqc(args)

    # if qc not disabled:
    #   - mutate config into structs/data appropriate for `args`
    #   ngsqc(args)

def ngsqc(args):
    """
    Front-end sub-command for NGS QA/QC pipeline analysis.
    Process all projects in all runs.

    Runs -> Projects -> Samples

    requires:
        (if not specified)
        Demux directory -> Named "$run_id + '_demux'"
        Sequencing directory -> Configured by server in src/Dmux/config.py
    """
    runs = utils.get_run_directories(args.rundir, seq_dir=args.seq_dir)
    utils.ensure_pe_adapters([run[1]['samplesheet'] for run in runs])

    configs = utils.base_qc_config()
    for (rundir, run_info) in runs:
        rid = run_info['run_id']
        this_demux_dir = Path(rundir, rid + '_demux')
        if not this_demux_dir.exists():
            raise FileNotFoundError('Demux data directory does not exist: ' + str(this_demux_dir))
        configs['demux_dir'].append(this_demux_dir)
        configs['run_ids'].append(rundir.name)
        sample_sheet = run_info['samplesheet']
        configs['sample_sheet'].append(str(sample_sheet.path.absolute()))
        configs['projects'].append(sample_sheet.samples[0].Sample_Project)
        sample_list = [
            dict(sid=sample.Sample_ID+'_S'+str(i), r1_adapter=sample.index, r2_adapter=sample.index2) 
            for i, sample in enumerate(sample_sheet.samples, start=1)
        ]
        configs['samples'].append(sample_list)
        configs['sids'].append([x['sid'] for x in sample_list])
        configs['rnums'].append(['1', '2'] if sample_sheet.is_paired_end else ['1'])
   
        out_base = Path(args.output).absolute() if args.output \
            else Path(rundir, f"{sample_sheet.Header['Experiment Name']}_ngsqc").absolute()
        
        configs['out_to'].append(out_base)

    utils.exec_ngsqc_pipeline(configs, dry_run=args.dry_run, local=args.local)


def logs(args):
    # 1. check if sqlite log exists, make if not exists, return empty log message
    # 2. given it exists, query log based on cli filters
    # 3. return log pretty message
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(prog='dmux')
    sub_parsers = main_parser.add_subparsers(help='run subcommand help')

    # ~~~ run[demux] subcommand ~~~
    parser_run = sub_parsers.add_parser('run')
    parser_run.add_argument('rundir', metavar='<run directory>', nargs="+", type=utils.valid_run_input, 
                            help='Full & complete run id (format YYMMDD_INSTRUMENTID_TIME_FLOWCELLID) or absolute paths')
    parser_run.add_argument('-s', '--seq_dir', metavar='<sequencing directory>', default=None, type=str,
                            help='Root directory for sequencing data (defaults for biowulf/bigsky/locus), must contain directories ' + \
                            'matching run ids, if not using full paths.')
    parser_run.add_argument('-o', '--output', metavar='<output directory>', default=None, type=str, 
                            help='Top-level output directory for demultiplexing data (defaults to input directory + runid + "_demux")')
    parser_run.add_argument('-d', '--dry-run', action='store_true',
                            help='Dry run the demultiplexing workflow')
    parser_run.add_argument('-l', '--local', action='store_true',
                            help='Execute pipeline locally without a dispatching executor')
    parser_run.set_defaults(func = run)

    # ~~~ ngsqc subcommand ~~~
    # TODO:
    #   - evaluate wheter or not to accept non-standard sample sheet names
    #   - evaluxwate wheter or not to accept non-standard demux directory
    parser_ngs_qc = sub_parsers.add_parser('ngsqc')
    parser_ngs_qc.add_argument('rundir', metavar='Run directory', nargs="+", type=utils.valid_run_input, 
                               help='Full & complete run id, no wildcards or regex (format YYMMDD_INSTRUMENTID_TIME_FLOWCELLID)')
    parser_ngs_qc.add_argument('-o', '--output', metavar='<output directory>', default=None, type=str)
    parser_ngs_qc.add_argument('-s', '--seq_dir', metavar='<sequencing directory>', default=None, type=str,
                            help='Root directory for sequencing data (defaults for biowulf/bigsky/locus), must contain directories ' + \
                            'matching run ids, if not using full paths.')
    parser_ngs_qc.add_argument('-d', '--dry-run', action='store_true',
                            help='Dry run the demultiplexing workflow')
    parser_ngs_qc.add_argument('-l', '--local', action='store_true',
                            help='Execute pipeline locally without a dispatching executor')
    parser_ngs_qc.set_defaults(func = ngsqc)

    # ~~~ logs subcommand ~~~
    parser_logs = sub_parsers.add_parser('logs', help='logs subcommand help')
    parser_logs.add_argument('Run', type=utils.valid_runid, 
                             help='Partial or full run id, can use wildcards')
    parser_logs.add_argument('--before', type=str, dest='before', default=None,
                             help='Only look at log results demultiplexed before this date (format MMDDYYYY)')
    parser_logs.add_argument('--after', type=str, dest='after', default=None,
                             help='Only look at log results demultiplexed after this date (format MMDDYYYY)')
    parser_logs.set_defaults(func = logs)

    args = main_parser.parse_args()
    args.func(args)