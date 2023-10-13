from Dmux.snk_utils import get_adapter_opts, fmt_input_flag_fastp


rule trim_w_fastp:
    input:
        adapters        = config['untrimmed_qc_dir'] + "/fastqc_adapters.txt",
        sample          = [config['demux_dir'] + "/" + config['projects'] + "/{sid}_R1_001.fastq.gz", 
                           config['demux_dir'] + "/" + config['projects'] + "/{sid}_R2_001.fastq.gz"],
    output:
        trimmed         = config['trim_dir'] + "/{sid}_trimmed.fastq.gz",
        unpaired1       = config['trim_dir'] + "/{sid}.u1.fastq.gz",
        unpaired2       = config['trim_dir'] + "/{sid}.u2.fastq.gz",
        merged          = config['trim_dir'] + "/{sid}.merged.fastq.gz",
        failed          = config['trim_dir'] + "/{sid}.failed.fastq.gz",
        html            = config['trim_dir'] + "/{sid}.html",
        json            = config['trim_dir'] + "/{sid}.json",
    params:
        adapters        = get_adapter_opts,
        extra           = "--merge",
        in_flag         = fmt_input_flag_fastp,
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    threads: 4
    resources: mem_mb = 8192
    log: config['trimmed_qc_dir'] + "/fastp_{sid}.log"
    shell:
        """
        conda run -n ngsqc fastp \
        {params.extra} \
        {params.adapters} \
        {params.in_flag} \
        --failed_out {output.failed} \
        --merged_out {output.merged} \
        --html {output.html} \
        --json {output.json} \
        """


rule fastq_screen:
    input:
        config['trim_dir'] + "/{sid}_trimmed.fastq.gz",
    output:
        txt             = config['trimmed_qc_dir'] + "/fastq_screen/{sid}.fastq_screen.txt",
        png             = config['trimmed_qc_dir'] + "/fastq_screen/{sid}.fastq_screen.png",
    params:
        fastq_screen_config="fastq_screen.conf",
        subset=1000000,
        aligner='bowtie2'
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    conda: "ngsqc"
    threads: 4
    resources: mem_mb = 8192
    log: config['trimmed_qc_dir'] + "/fastq_screen_{sid}.log"
    wrapper:
        "v2.6.0/bio/fastq_screen"
