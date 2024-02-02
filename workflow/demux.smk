import shutil


demux_expand_args = {
    "project": config["project"],
    "out_to": config["out_to"],
    "rid": config["run_ids"],
    "rnums": config["rnums"],
    "sids": config['sids'],
}
demux_noop_args = dict.fromkeys(demux_expand_args.keys(), [])


localrules: fastq_linker_from_dragen


rule bcl2fastq:
    """
        BCL to FASTQ file converter
        bcl2fastq v2.20.0.422
        Copyright (c) 2007-2017 Illumina, Inc.
    """
    input:
        run_dir                = config['demux_input_dir'] if not config['bclconvert'] else [],
        binary_base_calls      = expand("{files}", files=config['bcl_files'] if not config['bclconvert'] else demux_noop_args),
        samplesheet            = config["sample_sheet"] if not config['bclconvert'] else [],
    output:
        seq_data               = expand("{out_to}/demux/{project}/{sids}_R{rnums}_001.fastq.gz", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
        undetermined           = expand("{out_to}/demux/Undetermined_S0_R{rnums}_001.fastq.gz", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
        stats                  = expand("{out_to}/demux/Stats/Stats.json", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
        breadcrumb             = expand("{out_to}/demux/.B2F_DEMUX_COMPLETE", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
    params:
        out_dir                = config["out_to"] + "/demux",
    container: config["resources"]["sif"] + "bcl2fastq.sif",
    log: config["out_to"] + "/logs/bcl2fastq/" + config["run_ids"] + "_" + config["project"] + ".log",
    threads: 75
    resources: 
        mem_mb = int(64e3),
    shell: 
        """
            bcl2fastq \
            --sample-sheet {input.samplesheet} \
            --runfolder-dir {input.run_dir} \
            --min-log-level=TRACE \
            -r 16 -p 40 -w 16 \
            --fastq-compression-level 9 \
            --no-lane-splitting \
            -o {params.out_dir}
            touch {output.breadcrumb}
        """


rule bclconvert:
    """
    bcl-convert Version 00.000.000.4.2.4

    Run BCL Conversion (BCL directory to *.fastq.gz)
        bcl-convert --bcl-input-directory <BCL_ROOT_DIR> --output-directory <PATH> [options]

        --bcl-input-directory arg              Input BCL directory for BCL conversion (must be specified)
        --sample-sheet arg                     Path to SampleSheet.csv file (default searched for in --bcl-input-directory)
        --first-tile-only arg                  Only convert first tile of input (for testing & debugging)
        --bcl-sampleproject-subdirectories arg Output to subdirectories based upon sample sheet 'Sample_Project' column
        --sample-name-column-enabled arg       Use sample sheet 'Sample_Name' column when naming fastq files & subdirectories
        --fastq-gzip-compression-level arg     Set fastq output compression level 0-9 (default 1)
        --bcl-num-parallel-tiles arg           # of tiles to process in parallel (default 1)
        --bcl-num-conversion-threads arg       # of threads for conversion (per tile, default # cpu threads)
        --bcl-num-compression-threads arg      # of threads for fastq.gz output compression (per tile, default # cpu threads,
                                                or HW+12)
        --bcl-num-decompression-threads arg    # of threads for bcl/cbcl input decompression (per tile, default half # cpu 
                                                threads, or HW+8. Only applies when preloading files)
        --bcl-only-matched-reads arg           For pure BCL conversion, do not output files for 'Undetermined' [unmatched] 
                                                reads (output by default)
        --no-lane-splitting arg                Do not split FASTQ file by lane (false by default)

    """
    input:
        run_dir                = config['demux_input_dir'],
        binary_base_calls      = expand("{files}", files=config['bcl_files'] if config['bclconvert'] else demux_noop_args),
        samplesheet            = expand("{ss}", ss=config['sample_sheet'] if config['bclconvert'] else demux_noop_args),
        runinfo                = expand("{run}/RunInfo.xml", run=config['demux_input_dir'] if config['bclconvert'] else demux_noop_args),
    params:
        out_dir                = config["out_to"] + "/demux/",
        proj_dir               = config["out_to"] + "/demux/" + config["project"],
    output:
        seq_data               = expand("{out_to}/demux/{project}/{sids}_R{rnums}_001.fastq.gz", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        undetermined           = expand("{out_to}/demux/Undetermined_S0_R{rnums}_001.fastq.gz", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        stats                  = expand("{out_to}/demux/Reports/Demultiplex_Stats.csv", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        ametrics               = expand("{out_to}/demux/Reports/Quality_Metrics.csv", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        qmetrics               = expand("{out_to}/demux/Reports/Adapter_Metrics.csv", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        top_unknown            = expand("{out_to}/demux/Reports/Top_Unknown_Barcodes.csv", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        breadcrumb             = expand("{out_to}/demux/.BC_DEMUX_COMPLETE", **demux_expand_args if config['bclconvert'] else demux_noop_args),
    container: config["resources"]["sif"] + "weave_bclconvert_0.0.3.sif",
    threads: 75
    resources: mem_mb = int(64e3)
    shell:
        """
        bcl-convert \
        --bcl-input-directory {input.run_dir} \
        --force \
        --output-directory {params.out_dir} \
        --sample-sheet {input.samplesheet} \
        --fastq-gzip-compression-level 9 \
        --bcl-sampleproject-subdirectories true \
        --bcl-num-conversion-threads 24 \
        --bcl-num-compression-threads 24 \
        --bcl-num-decompression-threads 24 \
        --bcl-num-parallel-tiles 3 \
        --no-lane-splitting true
        touch {output.breadcrumb}
        """


rule fastq_linker_from_dragen:
    input:
        read1                  = expand(config["demux_input_dir"] + "/Analysis/1/Data/fastq/{full_sid}_R1_001.fastq.gz", full_sid=config["sids"]) if not config['demux_data'] else [],
        read2                  = expand(config["demux_input_dir"] + "/Analysis/1/Data/fastq/{full_sid}_R2_001.fastq.gz", full_sid=config["sids"]) if not config['demux_data'] else [],
        adapter_metrics        = config["demux_input_dir"] + "/Analysis/1/Data/Reports/Adapter_Metrics.csv" if not config['demux_data'] else [],
        qual_metrics           = config["demux_input_dir"] + "/Analysis/1/Data/Reports/Quality_Metrics.csv" if not config['demux_data'] else [],
        demux_stats            = config["demux_input_dir"] + "/Analysis/1/Data/Reports/Demultiplex_Stats.csv" if not config['demux_data'] else [],
    output:
        out_read1              = expand(config["out_to"] + "/demux/" + config["project"] + "/{full_sid}_R1_dragen.fastq.gz", full_sid=config["sids"]) if not config['demux_data'] else [],
        out_read2              = expand(config["out_to"] + "/demux/" + config["project"] + "/{full_sid}_R2_dragen.fastq.gz", full_sid=config["sids"]) if not config['demux_data'] else [],
        breadcrumb             = expand(config["out_to"] + "/demux/.breadcrumb/{full_sid}", full_sid=config["sids"]) if not config['demux_data'] else [],
        adapter_metrics_out    = config["out_to"] + "/demux/dragen_reports/Adapter_Metrics.csv" if not config['demux_data'] else [],
        qual_metrics_out       = config["out_to"] + "/demux/dragen_reports/Quality_Metrics.csv" if not config['demux_data'] else [],
        demux_stats_out        = config["out_to"] + "/demux/dragen_reports/Demultiplex_Stats.csv" if not config['demux_data'] else [],
    run:
        demux_dir = Path(config["out_to"], 'demux').resolve()
        bc_dir = Path(demux_dir, '.breadcrumb').resolve()
        if not bc_dir.exists():
            bc_dir.mkdir(mode=0o755)
        for r1, r2, sid in zip(input.read1, input.read2, config["sids"]):
            Path(demux_dir, config["project"], f"{sid}_R1_dragen.fastq.gz").absolute().symlink_to(Path(r1))
            Path(demux_dir, config["project"], f"{sid}_R2_dragen.fastq.gz").absolute().symlink_to(Path(r2))
            Path(bc_dir, sid).touch(mode=0o755)
        shutil.copyfile(input.adapter_metrics, output.adapter_metrics_out)
        shutil.copyfile(input.qual_metrics, output.qual_metrics_out)
        shutil.copyfile(input.demux_stats, output.demux_stats_out)

    