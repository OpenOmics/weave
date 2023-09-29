#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   module loading functions for the Dmux software package
# ~~~~~~~~~~~~~~~
from Dmux.config import get_current_server
from os import system, environ


host = get_current_server()


def init_demux_mods():
    if host == 'biowulf':
        try:
            if "__LMOD_REF_COUNT_PATH" in environ:
                environ["__LMOD_REF_COUNT_PATH"] = "/usr/local/current/singularity/3.10.5/bin:1;/usr/local/apps/snakemake/7.32.3/bin:1;" + environ['__LMOD_REF_COUNT_PATH']
            else:
                environ["__LMOD_REF_COUNT_PATH"] = "/usr/local/current/singularity/3.10.5/bin:1;/usr/local/apps/snakemake/7.32.3/bin:1;"

            if "__LMOD_REF_COUNT_MANPATH" in environ:
                environ["__LMOD_REF_COUNT_MANPATH"] = "/usr/local/current/singularity/3.10.5/share/man:1;" + environ['__LMOD_REF_COUNT_MANPATH']
            else:
                environ["__LMOD_REF_COUNT_MANPATH"] = "/usr/local/current/singularity/3.10.5/share/man:1;"

            if "_LMFILES_" in environ:
                environ["_LMFILES_"] = "/usr/local/lmod/modulefiles/snakemake/7.32.3.lua:/usr/local/lmod/modulefiles/singularity/3.10.5.lua:" +  environ["_LMFILES_"]
            else:
                environ["_LMFILES_"] = "/usr/local/lmod/modulefiles/snakemake/7.32.3.lua:/usr/local/lmod/modulefiles/singularity/3.10.5.lua:"

            if "MANPATH" in environ:
                environ["MANPATH"] = "/usr/local/current/singularity/3.10.5/share/man:" + environ["MANPATH"]
            else:
                environ["MANPATH"] = "/usr/local/current/singularity/3.10.5/share/man:"

            environ["PATH"] = "/usr/local/current/singularity/3.10.5/bin:/usr/local/apps/snakemake/7.32.3/bin:" + environ['PATH']
            update_vals = dict(LMOD_FAMILY_SINGULARITY = "singularity", \
                            biowulf_FAMILY_SINGULARITY = "singularity", LOADEDMODULES = "snakemake/7.32.3:singularity/3.10.5")
            environ.update(update_vals)
        finally:
            proc = 0
    else:
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
    