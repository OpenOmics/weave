demux_expand_args = {
    "project": config["project"],
    "out_to": config["out_to"],
    "rid": config["run_ids"],
    "rnums": config["rnums"],
    "sids": config['sids'],
}


rule bcl2fastq:
    """
        BCL to FASTQ file converter
        bcl2fastq v2.20.0.422
        Copyright (c) 2007-2017 Illumina, Inc.
    """
    input:
        run_dir                = config['demux_input_dir'],
        binary_base_calls      = expand("{files}", files=config['bcl_files']),
        samplesheets           = expand("{run}/SampleSheet.csv", run=config['demux_input_dir'])
    output:
        seq_data               = expand("{out_to}/demux/{rid}/{project}/{sids}_R{rnums}_001.fastq.gz", **demux_expand_args),
        undetermined           = expand("{out_to}/demux/Undetermined_S0_R{rnums}_001.fastq.gz", **demux_expand_args),
        stats                  = expand("{out_to}/demux/Stats/Stats.json", **demux_expand_args),
        breadcrumb             = expand("{out_to}/demux/.DEMUX_COMPLETE", **demux_expand_args),
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