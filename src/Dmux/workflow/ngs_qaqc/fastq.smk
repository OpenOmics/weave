from Dmux.snk_utils import get_adapter_opts
from Dmux.config import DIRECTORY_CONFIGS, get_current_server


server_config = DIRECTORY_CONFIGS[get_current_server()]


rule trim_w_fastp:
    input:
        adapters        = config['out_to'] + "/{project}/" + config['run_ids'] + "/fastqc_adapters.txt",
        in_read1        = config['demux_dir'] + "/{project}/{sid}_R1_001.fastq.gz",
        in_read2        = config['demux_dir'] + "/{project}/{sid}_R2_001.fastq.gz",
    output:
        html            = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}.html",
        json            = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_fastp.json",
        out_read1       = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R1.fastq.gz",
        out_read2       = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R2.fastq.gz",
    params:
        adapters        = get_adapter_opts,
    containerized: server_config["sif"] + "dmux_ngsqc_0.0.1.sif"
    threads: 4,
    resources: mem_mb = 8192,
    log: config['out_to'] + "/.logs/{project}/" + config['run_ids'] + "/fastp/{sid}.log",
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
        read                = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R{rnum}.fastq.gz",
    output:
        txt                 = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastq_screen/{sid}_trimmed_R{rnum}_screen.txt",
        png                 = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastq_screen/{sid}_trimmed_R{rnum}_screen.png",
        html                = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastq_screen/{sid}_trimmed_R{rnum}_screen.html",
    params:
        config_file         = "/etc/fastq_screen.conf",
        subset              = 1000000,
        aligner             = "bowtie2",
        output_dir          = lambda w: config['out_to'] + "/" + w.project + "/" + config['run_ids'] + "/" + w.sid + "/fastq_screen/",
    containerized: server_config["sif"] + "dmux_ngsqc_0.0.1.sif"
    threads: 4,
    resources: mem_mb = 8192,
    log: config['out_to'] + "/.logs/{project}/" + config['run_ids'] + "/fastq_screen/{sid}_R{rnum}.log",
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
        read1               = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R1.fastq.gz", 
        read2               = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R2.fastq.gz",
    output:
        kaiju_report        = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/kaiju/{sid}.tsv",
        kaiju_species       = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/kaiju/{sid}_species.tsv",
        kaiju_phylum        = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/kaiju/{sid}_phylum.tsv",
    params:
        # TODO: soft code these paths
        nodes               = "/data/OpenOmics/references/Dmux/kaiju/kaiju_db_nr_euk_2023-05-10/nodes.dmp",
        names               = "/data/OpenOmics/references/Dmux/kaiju/kaiju_db_nr_euk_2023-05-10/names.dmp",
        database            = "/data/OpenOmics/references/Dmux/kaiju/kaiju_db_nr_euk_2023-05-10/kaiju_db_nr_euk.fmi",
    containerized: server_config["sif"] + "dmux_ngsqc_0.0.1.sif"
    log: config['out_to'] + "/.logs/{project}/" + config['run_ids'] + "/kaiju/{sid}.log",
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
        kaiju2table -t {params.nodes} -n {params.names} -r species -o {output.kaiju_species} {output.kaiju_report}
        kaiju2table -t {params.nodes} -n {params.names} -r phylum -o {output.kaiju_phylum} {output.kaiju_report}
        """


rule kraken_annotation:
    input:
        read1               = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R1.fastq.gz", 
        read2               = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R2.fastq.gz",
    output:
        kraken_report       = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/kraken/{sid}.tsv",
        kraken_log          = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/kraken/{sid}.log",
    params:
        kraken_db           = "/data/OpenOmics/references/Dmux/kraken2/k2_pluspfp_20230605"
    containerized: server_config["sif"] + "dmux_ngsqc_0.0.1.sif"
    log: config['out_to'] + "/.logs/{project}/" + config['run_ids'] + "/kraken/{sid}.log",
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
