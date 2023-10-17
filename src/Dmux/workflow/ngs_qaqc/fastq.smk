from Dmux.snk_utils import get_adapter_opts


rule trim_w_fastp:
    input:
        adapters        = config['untrimmed_qc_dir'] + "/fastqc_adapters.txt",
        in_read1        = config['demux_dir'] + "/{project}/{sid}_R1_001.fastq.gz",
        in_read2        = config['demux_dir'] + "/{project}/{sid}_R2_001.fastq.gz",
    output:
        html            = config['trim_dir'] + "/{project}/{sid}.html",
        json            = config['trim_dir'] + "/{project}/{sid}.json",
        out_read1       = config['trim_dir'] + "/{project}/{sid}_trimmed_R1.fastq.gz",
        out_read2       = config['trim_dir'] + "/{project}/{sid}_trimmed_R2.fastq.gz",
    params:
        adapters        = get_adapter_opts,
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    threads: 4
    resources: mem_mb = 8192
    log: config['trimmed_qc_dir'] + "/fastp.{project}.{sid}.log"
    shell:
        """
        conda run -n ngsqc fastp \
        {params.adapters} \
        --in1 {input.in_read1} --in2 {input.in_read2} \
        --out1 {output.out_read1} \
        --out2 {output.out_read2} \
        --html {output.html} \
        --json {output.json} \
        """


rule fastq_screen:
    input:
        read                = config['trim_dir'] + "/{project}/{sid}_trimmed_R{rnum}.fastq.gz",
    output:
        txt                 = config['trimmed_qc_dir'] + "/fastq_screen/{sid}_{project}/{sid}_trimmed_R{rnum}_screen.txt",
        png                 = config['trimmed_qc_dir'] + "/fastq_screen/{sid}_{project}/{sid}_trimmed_R{rnum}_screen.png",
        html                = config['trimmed_qc_dir'] + "/fastq_screen/{sid}_{project}/{sid}_trimmed_R{rnum}_screen.html",
    params:
        config_file         = "/etc/fastq_screen.conf",
        subset              = 1000000,
        aligner             = "bowtie2",
        output_dir          = lambda w: config['trimmed_qc_dir'] + "/fastq_screen/" + w.sid + "_" + w.project + "/"
    container: "docker://rroutsong/dmux_ngsqc:0.0.1",
    threads: 4,
    resources: mem_mb = 8192,
    log: config['trimmed_qc_dir'] + "/fastq_screen.{project}.{sid}_R{rnum}.log",
    shell:
        """
            conda run -n ngsqc fastq_screen --outdir {params.output_dir} \
            --force \
            --aligner {params.aligner} \
            --conf {params.config_file} \
            --subset {params.subset} \
            --threads {threads} \
            {input.read}
        """
