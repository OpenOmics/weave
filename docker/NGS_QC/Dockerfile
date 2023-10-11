FROM condaforge/miniforge3:23.3.1-1
RUN conda config --add channels bioconda
RUN conda config --add channels conda-forge
RUN conda create -n ngsqc kraken2 kaiju fastp fastqc multiqc
# context dir needs to be repo root
ADD NGS_QC/docker/ep.sh /ep.sh
ADD NGS_QC/docker/fastq_screen.conf /etc/fastq_screen.conf
ENTRYPOINT [ "/ep.sh" ]