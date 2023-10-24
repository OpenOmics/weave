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
    resources: mem_mb = 8192,
    log: config['trimmed_qc_dir'] + "/fastp.{project}.{sid}.log"
    shell:
        """
        fastp \
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
            fastq_screen --outdir {params.output_dir} \
            --force \
            --aligner {params.aligner} \
            --conf {params.config_file} \
            --subset {params.subset} \
            --threads {threads} \
            {input.read}
        """


rule kaiju_annotation:
    input:
        read1               = config['trim_dir'] + "/{project}/{sid}_trimmed_R1.fastq.gz", 
        read2               = config['trim_dir'] + "/{project}/{sid}_trimmed_R2.fastq.gz", 
    output:
        kaiju_report        = config['trimmed_qc_dir'] + "/kaiju/{sid}_{project}/{sid}_kaiju_results.tsv",
    params:
        nodes               = "/gpfs/gsfs8/users/OpenOmics/references/Dmux/kaiju/kaiju_db_nr_euk_2023-05-10/nodes.dmp",
        database            = "/gpfs/gsfs8/users/OpenOmics/references/Dmux/kaiju/kaiju_db_nr_euk_2023-05-10/kaiju_db_nr_euk.fmi",
    container: "docker://rroutsong/dmux_ngsqc:0.0.1",
    log: config['trimmed_qc_dir'] + "/kaiju.{project}.{sid}.log",
    threads: 24
    resources: 
        mem_mb = 220000,
        slurm_partition = 'norm',
        runtime = 60*24*2
    shell:
        """
        kaiju \
        -t {params.nodes} \
        -f {params.database} \
        -i {input.read2} \
        -j {input.read1} \
        -z {threads} \
        -o {output.kaiju_report}
        """


rule kraken_annotation:
    input:
        read1               = config['trim_dir'] + "/{project}/{sid}_trimmed_R1.fastq.gz", 
        read2               = config['trim_dir'] + "/{project}/{sid}_trimmed_R2.fastq.gz", 
    output:
        kraken_report       = config['trimmed_qc_dir'] + "/kraken/{sid}_{project}/{sid}_kraken2.tsv",
        kraken_log          = config['trimmed_qc_dir'] + "/kraken/kraken2_stdout_{project}_{sid}.log",
    params:
        kraken_db           = "/data/OpenOmics/references/Dmux/kraken2/k2_pluspfp_20230605"
    container: "docker://rroutsong/dmux_ngsqc:0.0.1",
    log: config['trimmed_qc_dir'] + "/kraken2.{project}.{sid}.log",
    threads: 24
    resources: 
        mem_mb = 220000,
        slurm_partition = 'norm',
        runtime = 60*24*2
    shell:
        """
        kraken2 \
        --threads {threads} \
        --db {params.kraken_db} \
        --gzip-compressed --paired \
        --report {output.kraken_report} \
        --output {output.kraken_log} \
        {input.read1} \
        {input.read2}
        """
