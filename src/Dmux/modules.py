#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   module loading functions for the Dmux software package
# ~~~~~~~~~~~~~~~
from Dmux.config import get_current_server
from os import system


host = get_current_server()


def init_demux_mods():
    proc = system(get_demux_mods())
    return proc == 0


def get_demux_mods():
    mods_needed_for_demux = ['snakemake', 'singularity']
    mod_cmd = []

    if host == 'bigsky':
        mod_cmd.append('source /gs1/apps/user/rmlspack/share/spack/setup-env.sh')
        mod_cmd.append('spack load miniconda3@4.11.0')
    else:
        mod_cmd.append('module purge')
        mod_cmd.append(f"module load {' '.join(mods_needed_for_demux)}")

    return '; '.join(mod_cmd)


def close_demux_mods():
    if host == 'bigsky':
        p = system('despacktivate')
    else:
        p = system('module purge')
    return int(p) == 0
    