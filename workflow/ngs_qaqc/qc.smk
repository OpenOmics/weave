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
        samples     = expand("{demux_dir}/{project}/{sid}_R{rnum}_001.fastq.gz", demux_dir=config['demux_dir'], \
                                 project=config['projects'], sid=config['sids'], rnum=config['rnums']),
        adapters    = config['untrimmed_qc_dir'] + "/fastqc_adapters.txt",
    output:
        html        = expand("{qc_dir}/{sid}_R{rnum}_untrimmed.html", qc_dir=config['untrimmed_qc_dir'], \
                                 project=config['projects'], sid=config['sids'], rnum=config['rnums']),
        report      = expand("{qc_dir}/{sid}_R{rnum}_untrimmed_fastqc.zip", qc_dir=config['untrimmed_qc_dir'], \
                                 project=config['projects'], sid=config['sids'], rnum=config['rnums']),
    params:
        output_dir  = config['untrimmed_qc_dir']
    log: expand("{qc_dir}/{sid}_R{rnum}.log", qc_dir=config['untrimmed_qc_dir'], sid=config['sids'], rnum=config['rnums']),
    threads: 24
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    resources:
        mem_mb = 32768
    shell:
        "conda run -n ngsqc fastqc -o {params.output_dir} -a {input.adapters} -t {threads} {input.samples}"
   

rule fastqc_trimmed:
    input:
        samples     = expand("{trim_dir}/{sid}_trimmed.fastq.gz", trim_dir=config['trim_dir'], sid=config['sids']),
    output:
        html        = expand("{trim_qc_dir}/{sid}_trimmed.html", trim_qc_dir=config['trimmed_qc_dir'], sid=config['sids']),
        report      = expand("{trim_qc_dir}/{sid}_trimmed_fastqc.zip", trim_qc_dir=config['trimmed_qc_dir'], sid=config['sids']),
    params:
        output_dir  = config['trimmed_qc_dir']
    container: "docker://rroutsong/dmux_ngsqc:0.0.1"
    threads: 24
    resources:
        mem_mb = 32768
    log: config['trimmed_qc_dir'] + "/fastqc_post_trim.log"
    shell:
        "conda run -n ngsqc fastqc -o {params.output_dir} -t {threads} {input.samples}"