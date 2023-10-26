from Dmux.config import DIRECTORY_CONFIGS, get_current_server


server_config = DIRECTORY_CONFIGS[get_current_server()]


rule index_annotations:
    input:
        sample_sheet    = expand("{sheet}", sheet=config['sample_sheet']),
        read            = expand("{demux_dir}/{project}/{sid}_R{rnum}_001.fastq.gz", demux_dir=config['demux_dir'], \
                                 project=config['projects'], sid=config['sids'], rnum=config['rnums']),
    output:
        fastqc_adapters = expand("{outdir}/{project}/{rid}/fastqc_adapters.txt", outdir=config['out_to'], 
        project=config['projects'], \
                                 rid=config['run_ids'])
    log: config['out_to'] + "/.logs/index_annotations.log"
    localrule: True
    run:
        shell(f"mkdir -p {config['out_to']}/{config['run_ids']}")
        ss = SampleSheet(config['sample_sheet'])
        for i, samp in enumerate(ss.samples, start=1):
            shell(f"echo \"{samp.Sample_ID}_R1\t{samp.index}\" >> {config['out_to']}/{config['projects']}/{config['run_ids']}/fastqc_adapters.txt")
            if ss.is_paired_end:
                shell(f"echo \"{samp.Sample_ID}_R2\t{samp.index2}\" >> {config['out_to']}/{config['projects']}/{config['run_ids']}/fastqc_adapters.txt")


rule fastqc_untrimmed:
    input:
        samples     = config['demux_dir'] + "/{project}/{sid}_R{rnum}_001.fastq.gz",
        adapters    = config['out_to'] + "/{project}/" + config['run_ids'] + "/fastqc_adapters.txt",
    output:   
        html        = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastqc_untrimmed/{sid}_R{rnum}_001_fastqc.html",
        fqreport    = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastqc_untrimmed/{sid}_R{rnum}_001_fastqc.zip",
    params:
        output_dir  = lambda w: config['out_to'] + "/" + w.project + "/" + config['run_ids'] + "/" + w.sid + "/fastqc_untrimmed/"
    log: config['out_to'] + "/.logs/{project}/" + config['run_ids'] + "/fastqc_untrimmed/{sid}_R{rnum}.log"
    threads: 4
    containerized: server_config["sif"] + "dmux_ngsqc_0.0.1.sif"
    resources: mem_mb = 8096
    shell:
        """
        mkdir -p {params.output_dir}
        fastqc -o {params.output_dir} -a {input.adapters} -t {threads} {input.samples}
        """
   

rule fastqc_trimmed:
    input:
        in_read     = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastp/{sid}_trimmed_R{rnum}.fastq.gz",
    output:
        html        = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastqc_trimmed/{sid}_trimmed_R{rnum}_fastqc.html",
        fqreport    = config['out_to'] + "/{project}/" + config['run_ids'] + "/{sid}/fastqc_trimmed/{sid}_trimmed_R{rnum}_fastqc.zip",
    params:
        output_dir  = lambda w: config['out_to'] + "/" + w.project + "/" + config['run_ids'] + "/" + w.sid + "/fastqc_trimmed/"
    containerized: server_config["sif"] + "dmux_ngsqc_0.0.1.sif"
    threads: 4
    resources: mem_mb = 8096
    log: config['out_to'] + "/.logs/{project}/" + config['run_ids'] + "/fastqc_trimmed/{sid}_R{rnum}.log"
    shell:
        """
        mkdir -p {params.output_dir}
        fastqc -o {params.output_dir} -t {threads} {input.in_read}
        """


rule multiqc_report:
    input:
        # fastqc on untrimmed reads
        expand("{out_dir}/{project}/{rid}/{sids}/fastqc_untrimmed/{sids}_R{rnum}_001_fastqc.zip", out_dir=config['out_to'], 
               project=config['projects'], rid=config['run_ids'], sids=config['sids'], rnum=config['rnums']),
        # fastqc on trimmed reads
        expand("{out_dir}/{project}/{rid}/{sids}/fastqc_trimmed/{sids}_trimmed_R{rnum}_fastqc.zip", out_dir=config['out_to'], 
               sids=config['sids'], project=config['projects'], rid=config['run_ids'], rnum=config['rnums']),
        # fastp trimming metrics
        expand("{out_dir}/{project}/{rid}/{sids}/fastp/{sids}_trimmed_R{rnum}.fastq.gz", out_dir=config['out_to'], 
               sids=config['sids'], project=config['projects'], rid=config['run_ids'], rnum=config['rnums']),
        # fastq screen
        expand("{out_dir}/{project}/{rid}/{sids}/fastq_screen/{sids}_trimmed_R{rnum}_screen.html", out_dir=config['out_to'], 
               sids=config['sids'], rnum=config['rnums'], rid=config['run_ids'], project=config['projects']),
        # kraken2
        expand("{out_dir}/{project}/{rid}/{sids}/kraken/{sids}.tsv", out_dir=config['out_to'], sids=config['sids'], 
               project=config['projects'], rid=config['run_ids']),
        # kaiju
        expand("{out_dir}/{project}/{rid}/{sids}/kaiju/{sids}.tsv", out_dir=config['out_to'], sids=config['sids'], 
               project=config['projects'], rid=config['run_ids']),
    output:
        mqc_report      = f"{config['out_to']}/{config['projects']}/{config['run_ids']}" + \
                           "/multiqc/Run-" +  config['run_ids'] + \
                           "-Project-" +  config['projects'] + "_multiqc_report.html"
    params:
        input_dir       = config['out_to'],
        demux_dir       = config['demux_dir'],
        output_dir      = config['out_to'] + "/" + config['projects'] + "/" + config['run_ids'] + "/multiqc/",
        report_title    = f"Run: {config['run_ids']}, Project: {config['projects']}",
    containerized: "/data/OpenOmics/SIFs/dmux_ngsqc_0.0.1.sif"
    threads: 4
    resources: mem_mb = 8096
    log: config['out_to'] + "/.logs/" + config['projects'] + "/" + config['run_ids'] + "/multiqc/multiqc.log"
    shell:
        """
        multiqc -q -ip \
        --title \"{params.report_title}\" \
        -o {params.output_dir} \
        {params.input_dir} {params.demux_dir} \
        --ignore ".cache" --ignore ".config" --ignore ".snakemake" --ignore ".slurm" --ignore ".singularity" --ignore ".logs"
        """
