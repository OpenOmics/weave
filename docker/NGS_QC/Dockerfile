FROM ubuntu:latest
ENV TZ=America/New_York
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update; apt-get upgrade -y bash && \
    apt-get install -y fastqc python-is-python3 rna-star bwa hisat2 python3-pip samtools multiqc fastp kraken2 bowtie2 libgd-graph-perl git curl libz-dev build-essential
RUN mkdir /opt2; curl -S -s -L https://github.com/StevenWingett/FastQ-Screen/archive/refs/tags/v0.15.3.tar.gz --output /opt2/v0.15.3.tar.gz
RUN cd /opt2 && tar xvf v0.15.3.tar.gz 
RUN cd /opt2 && git clone https://github.com/bioinformatics-centre/kaiju.git 
RUN cd /opt2/kaiju/src; make
RUN cd /opt2 && git clone https://github.com/AstraZeneca-NGS/disambiguate.git
RUN pip install pysam
RUN chmod +x /opt2/disambiguate/disambiguate.py; ln -sf /opt2/disambiguate/disambiguate.py /usr/bin/disambiguate.py
ENV PATH="${PATH}:/opt2/FastQ-Screen-0.15.3:/opt2/kaiju/bin"
ADD docker/NGS_QC/fastq_screen.conf /etc/fastq_screen.conf
