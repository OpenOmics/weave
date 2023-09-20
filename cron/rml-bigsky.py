#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ~~~~~~~~~~~~~~~
#   cron job script for use on RML's BigSky system,
#   intended to be run at any frequency but recommendation is once daily
#   search the run directory, identify directories by lock or date, 
#   stage the sample sheet, and kick off the 
# ~~~~~~~~~~~~~~~
from Dmux.files import get_all_seq_dirs
from Dmux.config import DIRECTORY_CONFIGS

SERVER_NAME = 'bigsky'
SEQUENCING_DIR = DIRECTORY_CONFIGS[SERVER_NAME]['seq']


def main():
    pass


if __name__ == '__main__':
    main()