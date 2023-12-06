demux_expand_args = {
    "project": config["project"],
    "out_to": config["out_to"],
    "rid": config["run_ids"],
    "rnums": config["rnums"],
    "sids": config['sids'],
}
demux_noop_args = dict.fromkeys(demux_expand_args.keys(), [])

rule bcl2fastq:
    """
        BCL to FASTQ file converter
        bcl2fastq v2.20.0.422
        Copyright (c) 2007-2017 Illumina, Inc.
    """
    input:
        run_dir                = config['demux_input_dir'],
        binary_base_calls      = expand("{files}", files=config['bcl_files'] if not config['bclconvert'] else demux_noop_args),
        samplesheets           = expand("{run}/SampleSheet.csv", run=config['demux_input_dir'] if not config['bclconvert'] else demux_noop_args)
    output:
        seq_data               = expand("{out_to}/demux/{rid}/{project}/{sids}_R{rnums}_001.fastq.gz", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
        undetermined           = expand("{out_to}/demux/Undetermined_S0_R{rnums}_001.fastq.gz", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
        stats                  = expand("{out_to}/demux/Stats/Stats.json", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
        breadcrumb             = expand("{out_to}/demux/.B2F_DEMUX_COMPLETE", **demux_expand_args if not config['bclconvert'] else demux_noop_args),
    params:
        out_dir                = config["out_to"] + "/demux/",
        run                    = config["run_ids"],
        project                = config["project"],
    container: config["resources"]["sif"] + "bcl2fastq.sif",
    threads: 24
    shell: 
        r"""
            mkdir -p {params.out_dir}
            bcl2fastq \
            --runfolder-dir {input.run_dir} \
            --min-log-level=INFO \
            -r {threads} -p {threads} -w {threads} \
            --no-lane-splitting -o {params.out_dir}
            echo "run dir: {params.out_dir}/{params.run}/{params.project}"
            echo "proj dir: {params.out_dir}/{params.project}"
            mkdir -p {params.out_dir}/{params.run}
            mv {params.out_dir}/{params.project} {params.out_dir}/{params.run}
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
        samplesheets           = expand("{run}/SampleSheet.csv", run=config['demux_input_dir'] if config['bclconvert'] else demux_noop_args),
        runinfo                = expand("{run}/RunInfo.xml", run=config['demux_input_dir'] if config['bclconvert'] else demux_noop_args),
    params:
        out_dir                = config["out_to"] + "/demux/",
        run                    = config["run_ids"],
        project                = config["project"],
        mv_dir                 = config["out_to"] + "/demux/" + config["run_ids"] + "/" + config["project"]
    output:
        seq_data               = expand("{out_to}/demux/{rid}/{project}/{sids}_R{rnums}_001.fastq.gz", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        undetermined           = expand("{out_to}/demux/Undetermined_S0_R{rnums}_001.fastq.gz", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        stats                  = expand("{out_to}/demux/Reports/Demultiplex_Stats.csv", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        metrics                = expand("{out_to}/demux/Reports/Adapter_Metrics.csv", **demux_expand_args if config['bclconvert'] else demux_noop_args),
        breadcrumb             = expand("{out_to}/demux/.BC_DEMUX_COMPLETE", **demux_expand_args if config['bclconvert'] else demux_noop_args),
    container: config["resources"]["sif"] + "weave_bclconvert_0.0.3.sif",
    threads: 24
    shell:
        """
        bcl-convert \
        --bcl-input-directory {input.run_dir} \
        --force \
        --output-directory {params.out_dir} \
        --fastq-gzip-compression-level 9 \
        --bcl-sampleproject-subdirectories true \
        --bcl-num-conversion-threads 8 \
        --bcl-num-compression-threads 8 \
        --bcl-num-decompression-threads 8 \
        --bcl-num-parallel-tiles 3 \
        --no-lane-splitting true
        mkdir -p {params.mv_dir}
        mv {params.out_dir}/*.fastq.gz {params.mv_dir}
        touch {output.breadcrumb}
        """