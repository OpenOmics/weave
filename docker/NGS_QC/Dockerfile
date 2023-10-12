FROM condaforge/miniforge3:23.3.1-1
RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge
RUN conda create -n ngsqc kraken2 kaiju fastp fastqc multiqc bowtie2 fastq-screen
RUN apt-get update; apt-get upgrade -y bash
# context dir needs to be repo root
ADD /docker/NGS_QC/ep.sh /ep.sh
ADD /docker/NGS_QC/fastq_screen.conf /etc/fastq_screen.conf
RUN chmod u+x /ep.sh
ENTRYPOINT ["bash", "--rcfile", "/ep.sh", "-ce"]
