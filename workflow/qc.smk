qc_expand_args = {
    "rnums": config["rnums"],
    "sids": config['sids'],
}


if not config['demux_data']:
    trim_input_suffix = 'dragen'
    demux_stats = config["out_to"] + "/demux/dragen_reports/Demultiplex_Stats.csv"
else:
    trim_input_suffix = '001'
    if config['bclconvert']:
        demux_stats = config['out_to'] + "/demux/Reports/Demultiplex_Stats.csv"
    else:
        demux_stats = config['out_to'] + "/demux/Stats/Stats.json"
    

rule fastqc_untrimmed:
    input:
        samples     = config['out_to'] + "/demux/" + config["project"] + "/{sids}_R{rnums}_" + trim_input_suffix + ".fastq.gz",
    output:   
        html        = config['out_to'] + "/" + config["project"] + "/{sids}/fastqc_untrimmed/{sids}_R{rnums}_" + trim_input_suffix + "_fastqc.html",
        fqreport    = config['out_to'] + "/" + config["project"] + "/{sids}/fastqc_untrimmed/{sids}_R{rnums}_" + trim_input_suffix + "_fastqc.zip",
    params:
        output_dir  = lambda w: config['out_to'] + "/" + config["project"] + "/" + w.sids + "/fastqc_untrimmed/"
    log: config['out_to'] + "/logs/" + "/" + config["project"] + "/fastqc_untrimmed/{sids}_R{rnums}.log"
    threads: 4
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif"
    resources: mem_mb = 8096
    shell:
        """
        mkdir -p {params.output_dir}
        fastqc -o {params.output_dir} -t {threads} {input.samples}
        """
   

rule fastqc_trimmed:
    input:
        in_read     = config["out_to"] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R{rnums}.fastq.gz",
    output:
        html        = config['out_to'] + "/" + config["project"] + "/{sids}/fastqc_trimmed/{sids}_trimmed_R{rnums}_fastqc.html",
        fqreport    = config['out_to'] + "/" + config["project"] + "/{sids}/fastqc_trimmed/{sids}_trimmed_R{rnums}_fastqc.zip",
    params:
        output_dir  = lambda w: config['out_to'] + "/" + config["project"] + "/" + w.sids + "/fastqc_trimmed/"
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif"
    threads: 4
    resources: mem_mb = 8096
    log: config['out_to'] + "/logs/" + config["project"] + "/fastqc_trimmed/{sids}_R{rnums}.log"
    shell:
        """
        mkdir -p {params.output_dir}
        fastqc -o {params.output_dir} -t {threads} {input.in_read}
        """


rule multiqc_report:
    input:
        # demux status
        demux_stats,
        # fastqc on untrimmed reads
        expand(config['out_to'] + "/" + config["project"] + "/{sids}/fastqc_untrimmed/{sids}_R{rnums}_" + trim_input_suffix + "_fastqc.zip", **qc_expand_args),
        # fastqc on trimmed reads
        expand(config['out_to'] + "/" + config["project"] + "/{sids}/fastqc_trimmed/{sids}_trimmed_R{rnums}_fastqc.zip", **qc_expand_args),
        # fastp trimming metrics
        expand(config['out_to'] + "/" + config["project"] + "/{sids}/fastp/{sids}_trimmed_R{rnums}.fastq.gz", **qc_expand_args),
        # fastq screen
        expand(config['out_to'] + "/" + config["project"] + "/{sids}/fastq_screen/{sids}_trimmed_R{rnums}_screen.html", **qc_expand_args),
        # kraken2
        expand(config['out_to'] + "/" + config["project"] + "/{sids}/kraken/{sids}.tsv", **qc_expand_args),
        # kaiju
        expand(config['out_to'] + "/" + config["project"] + "/{sids}/kaiju/{sids}.tsv", **qc_expand_args),
    output:
        mqc_report      = expand(config['out_to'] + "/{project}" + \
                           "/multiqc/Run-{rid}-Project-{project}_multiqc_report.html",
                           project=config['project'], rid=config['run_ids']),
    params:
        input_dir       = config['out_to'],
        output_dir      = config['out_to'] + "/" + config["project"] + "/multiqc/",
        report_title    = "Run: " + config["run_ids"] + ", Project: " + config["project"],
    containerized: config["resources"]["sif"] + "weave_ngsqc_0.0.1.sif"
    threads: 4
    resources: mem_mb = 8096
    log: 
        expand(
            config['out_to'] + "/logs/multiqc/multiqc_{rid}_{project}.log", 
            project=config['project'], rid=config['run_ids']
        )
    shell:
        """
        multiqc -q -ip \
        --title \"{params.report_title}\" \
        -o {params.output_dir} \
        {params.input_dir} \
        --ignore ".cache" --ignore ".config" --ignore ".snakemake" --ignore ".slurm" --ignore ".singularity" --ignore ".logs"
        """
