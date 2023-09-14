#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   file system helper function for the Dmux software package
# ~~~~~~~~~~~~~~~
from pathlib import Path
from os import access as check_access, R_OK


def get_all_seq_dirs(top_dir):
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
    return list(filter(is_dir_staged, _dirs))


def is_dir_staged(run_dir):
    """
        filter check for wheter or not a directory has the appropriate breadcrumbs or not

        RTAComplete.txt - file transfer from instrument breadcrumb, CSV file with values:
            Run Date, Run time, Instrument ID
    """
    TRANSFER_BREADCRUMB = 'RTAComplete.txt'

    analyzed_checks = [
        Path(run_dir, TRANSFER_BREADCRUMB).exists()
    ]
    return all(analyzed_checks)