rule index_annotations:
    input:
        sample_sheet    = expand("{sheet}", sheet=config['sample_sheet']),
        read            = expand("{demux_dir}/{project}/{sid}_R{rnum}_001.fastq.gz", demux_dir=config['demux_dir'], \
                                 project=config['projects'], sid=config['sids'], rnum=config['rnums']),
    output:
        fastqc_adapters = expand("{untrimmed_qc_dir}/fastqc_adapters.txt", untrimmed_qc_dir=config['untrimmed_qc_dir'])
    log: config['untrimmed_qc_dir'] + "/index_annotations.log"
    localrule: True
    run:
        ss = SampleSheet(config['sample_sheet'])
        for i, samp in enumerate(ss.samples, start=1):
            shell(f"echo \"{samp.Sample_ID}_R1\t{samp.index}\" >> {config['untrimmed_qc_dir']}/fastqc_adapters.txt")
            if ss.is_paired_end:
                shell(f"echo \"{samp.Sample_ID}_R2\t{samp.index2}\" >> {config['untrimmed_qc_dir']}/fastqc_adapters.txt")


rule fastqc_untrimmed:
    input:
        samples     = config['demux_dir'] + "/{project}/{sid}_R{rnum}_001.fastq.gz",
        adapters    = config['untrimmed_qc_dir'] + "/fastqc_adapters.txt",
    output:
        html        = config['untrimmed_qc_dir'] + "/{project}/{sid}_R{rnum}_001_fastqc.html",
        report      = config['untrimmed_qc_dir'] + "/{project}/{sid}_R{rnum}_001_fastqc.zip",
    params:
        output_dir  = lambda w: config['untrimmed_qc_dir'] + "/" + w.project 
    log: config['untrimmed_qc_dir'] + "/logs/{project}/{sid}_R{rnum}.log"
    threads: 4
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    resources: mem_mb = 8096
    shell:
        "fastqc -o {params.output_dir} -a {input.adapters} -t {threads} --memory 7500 {input.samples}"
   

rule fastqc_trimmed:
    input:
        in_read     = config['trim_dir'] + "/{project}/{sid}_trimmed_R{rnum}.fastq.gz",
    output:
        html        = config['trimmed_qc_dir'] + "/{project}/{sid}_trimmed_R{rnum}_fastqc.html",
        report      = config['trimmed_qc_dir'] + "/{project}/{sid}_trimmed_R{rnum}_fastqc.zip",
    params:
        output_dir  = lambda w: config['trimmed_qc_dir'] + "/" + w.project
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    threads: 4
    resources: mem_mb = 8096
    log: config['trimmed_qc_dir'] + "/logs/{project}.{sid}_R{rnum}.log"
    shell:
        "fastqc -o {params.output_dir} -t {threads} {input.in_read}"
