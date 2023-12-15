FROM ubuntu:23.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get -qq update; apt-get -qq install pstack gdb wget vim curl alien
WORKDIR "/"
RUN wget -q https://hpc.nih.gov/~OpenOmics/weave/bcl-convert-4.2.4-2.el7.x86_64.rpm
RUN alien --scripts bcl-convert-4.2.4-2.el7.x86_64.rpm
RUN dpkg -i bcl-convert_4.2.4-3_amd64.deb
RUN mkdir /work; chmod -R 777 /work
WORKDIR "/work"
