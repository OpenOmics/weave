if not config['demux_data']:
    trim_input_affix = 'dragen'
else:
    trim_input_affix = '001'


rule trim_w_fastp:
    input:
        in_read1        = config["out_to"] + "/demux/" + config["project"] + "/{sids}_R1_" + trim_input_affix + ".fastq.gz",
        in_read2        = config["out_to"] + "/demux/" + config["project"] + "/{sids}_R2_" + trim_input_affix + ".fastq.gz" if len(config['rnums']) == 2 else [],
    output:
        html            = config["out_to"] + "/" + config["project"] + "/{sids}/fastp/{sids}.html",
        json            = config["out_to"] + "/" + config["project"] + "/{sids}/fastp/{sids}_fastp.json",
        out_read1       = config["out_to"] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R1.fastq.gz",
        out_read2       = config["out_to"] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R2.fastq.gz" if len(config['rnums']) == 2 else [],
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif"
    threads: 4,
    params:
        read_args = lambda _, output, input: f"--in2 {input.in_read2} --out2 {output.out_read2} --detect_adapter_for_pe""" if len(config['rnums']) == 2 else ""
    resources: mem_mb = 8192,
    log: config["out_to"] + "/logs/" + config["project"] + "/fastp/{sids}.log",
    shell:
        """
        fastp \
        --in1 {input.in_read1} --out1 {output.out_read1} {params.read_args} \
        --html {output.html} \
        --json {output.json} \
        """


rule fastq_screen:
    input:
        read                = config['out_to'] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R{rnum}.fastq.gz",
    output:
        txt                 = config['out_to'] + "/" + config["project"] + "/{sids}/fastq_screen/{sids}_trimmed_R{rnum}_screen.txt",
        png                 = config['out_to'] + "/" + config["project"] + "/{sids}/fastq_screen/{sids}_trimmed_R{rnum}_screen.png",
        html                = config['out_to'] + "/" + config["project"] + "/{sids}/fastq_screen/{sids}_trimmed_R{rnum}_screen.html",
    params:
        config_file         = "/etc/fastq_screen.conf",
        subset              = 1000000,
        aligner             = "bowtie2",
        output_dir          = lambda w: config['out_to'] + "/" + config["project"] + "/" + w.sids + "/fastq_screen/",
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif"
    threads: 4,
    resources: mem_mb = 8192,
    log: config['out_to'] + "/logs/" + config["project"] + "/fastq_screen/{sids}_R{rnum}.log",
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
        read1               = config['out_to'] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R1.fastq.gz", 
        read2               = config['out_to'] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R2.fastq.gz" if len(config['rnums']) == 2 else [],
    output:
        kaiju_report        = config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}.tsv",
        kaiju_order         = config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}_order.tsv",
        kaiju_family        = config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}_family.tsv",
        kaiju_species       = config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}_species.tsv",
        kaiju_phylum        = config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}_phylum.tsv",
        kaiju_genus         = config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}_genus.tsv",
    params:
        nodes               = config["resources"]["mounts"]["kaiju"]["to"] + "/nodes.dmp",
        names               = config["resources"]["mounts"]["kaiju"]["to"] + "/names.dmp",
        database            = config["resources"]["mounts"]["kaiju"]["to"] + "/kaiju_db_nr_euk.fmi",
        reads_in_arg        = lambda wc, input, output: f"-j {input.read1} -i {input.read2}" if input.read2 else f"-i {input.read1}",
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif"
    log: config['out_to'] + "/logs/" + config["project"] + "/kaiju/{sids}.log",
    threads: 24
    resources: 
        mem_mb = 220000, 
        runtime = 60*24*2
    shell:
        """
        kaiju \
        -t {params.nodes} \
        -f {params.database} \
        {params.reads_in_arg} \
        -z {threads} \
        -o {output.kaiju_report}
        kaiju2table -t {params.nodes} -n {params.names} -r species -o {output.kaiju_species} {output.kaiju_report}
        kaiju2table -t {params.nodes} -n {params.names} -r phylum -o {output.kaiju_phylum} {output.kaiju_report}
        kaiju2table -t {params.nodes} -n {params.names} -r family -o {output.kaiju_order} {output.kaiju_report}
        kaiju2table -t {params.nodes} -n {params.names} -r order -o {output.kaiju_family} {output.kaiju_report}
        kaiju2table -t {params.nodes} -n {params.names} -r genus -o {output.kaiju_genus} {output.kaiju_report}
        """


rule kraken_annotation:
    input:
        read1               = config['out_to'] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R1.fastq.gz", 
        read2               = config['out_to'] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R2.fastq.gz" if len(config['rnums']) == 2 else [],
    output:
        kraken_report       = config['out_to'] + "/" + config["project"] + "/{sids}/kraken/{sids}.tsv",
        kraken_log          = config['out_to'] + "/" + config["project"] + "/{sids}/kraken/{sids}.log",
    params:
        kraken_db           = config["resources"]["mounts"]["kraken2"]["to"],
        reads_in_arg        = lambda wc, input, output: f"{input.read1} {input.read2}" if input.read2 else f"{input.read1}",
        ended_arg           = lambda wc, input, output: "--paired " if input.read2 else "",
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif",
    log: config['out_to'] + "/logs/" + config["project"] + "/kraken/{sids}.log",
    threads: 24
    resources: 
        mem_mb = 220000,
        runtime = 60*24*2
    shell:
        """
        kraken2 \
        --threads {threads} \
        --db {params.kraken_db} \
        --gzip-compressed {params.ended_arg}\
        --report {output.kraken_report} \
        --output {output.kraken_log} \
        {params.reads_in_arg}
        """
