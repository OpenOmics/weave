# Introduction

This repository was created to contain the demultiplexing, sample sheet generation, and analysis workflow 
initialization workflows that exist across the NIH.gov infrastructures.

# Operation
__*REQUIREMENT*: manual run execution entry point__
Some developing options for determining how to find run directories:
- datetime.now(), query the top directory of the NGS data, directories younger now - day.
- placing .lock files as breadcrumbs and walking directories for ones without them

Logging would be essential, some ideas about it's operation:
- sqlite to catalogue what runs have been analyzed and has not + bread crumb lock
- log entry point in script that gives last 10 or so entries
- not entirely nailed down what all to store, some obvious meta information:
    - run id, directory, run time, exit code, outputs, execution start, execution stop, manual/automatic execution

# Software design & development plan (SDDP)

The value add of this software is still unclear as a modular drop-in system or a one-shot temporary solution. 
This can be as simple as some lines in bash that are engineered to
the four things needed with this workflow:
    - demultiplex (from bespoke instruments to a modular system with configurations for multiple sequencing platforms)
    - generate a sample sheet from this directory and LIMS (labkey is the initial use-case, but do we support others)
    - trigger the OpenOmics pipelines for analysis

Or as complex as a workflow that supports drop in configurations for different instruments and clusters, and 
in-between those two extremes. 

The idea we will begin with is to start as a simplistic system with anticipation of building in modularity, and the code 
will be written in such a way to embrace that modularity as best as possible with forward thinking kept in mind. If we
don't find utility in this work at a brace scale then we will accept the simple approach as bespoke and move forward.

# Requirements

Requirements for this software should be minimal. Python 3.6+, potentially some python libraries, a cron daemon, and a 
user account with crontab access.