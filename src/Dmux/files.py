#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   file system helper functions for the Dmux software package
# ~~~~~~~~~~~~~~~
from pathlib import Path
from os import access as check_access, R_OK
from functools import partial
from Dmux.labkey import LabKeyServer
from Dmux.config import LABKEY_CONFIGS


def get_all_seq_dirs(top_dir, server):
    """
        Gather and return all sequencing directories from the `top_dir`. 
        This is tightly coupled at the moment to the directory that is on RML-BigSky.
        In the future will need to the take a look at how to do this more generally
    """
    if isinstance(top_dir, str): top_dir = Path(top_dir)
    _dirs = []
    for _file in top_dir.glob('*'):
        if _file.is_dir():
            for _file2 in _file.glob('*'):
                if _file2.is_dir() and check_access(_file2, R_OK):
                    _dirs.append(_file2.resolve())
    # check if directory is processed or not
    return list(filter(partial(is_dir_staged, server), _dirs))


def is_dir_staged(server, run_dir):
    """
        filter check for wheter or not a directory has the appropriate breadcrumbs or not

        RTAComplete.txt - file transfer from instrument breadcrumb, CSV file with values:
            Run Date, Run time, Instrument ID

        
    """
    global LABKEY_CONFIGS
    this_labkey_project = LABKEY_CONFIGS[server]['container_path']
    TRANSFER_BREADCRUMB = 'RTAComplete.txt'
    SS_SHEET_EXISTS = LabKeyServer.runid2samplesheeturl(server, this_labkey_project, run_dir.name)

    analyzed_checks = [
        Path(run_dir, TRANSFER_BREADCRUMB).exists(),
        SS_SHEET_EXISTS is not None
    ]
    return all(analyzed_checks)


def is_dir_analyzed(run_dir):
    """
        Intention with this function is to take in a directory, and return a boolean on wheter it has been
        analyzed or not.

        TODO: Not totally sure how analysis breadcrumb have worked or will work....
    """
    return