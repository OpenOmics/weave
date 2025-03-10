## Objective

`weave`'s `run` subcommand is the command line entrypoint for execution of the Illumnia demultiplexing and FASTQ QC/QA pipeline. 

Given a run id or run directory containing the artifacts produced by Illumnia MiSeq/NextSeq/HiSeq instruments (RTAComplete.txt) this workflow will
demultiplex all the reads and run an array of tools for evaluating the qualitying of the sequenced reads.

The ultimate output for this workflow is a [MultiQC](https://multiqc.info/examples/rna-seq/multiqc_report) report containing all the
subsequent metrics from the QC/QA portions of the pipeline. 

The penultimate output for this workflow is a cohort of [fastq.gz](https://knowledge.illumina.com/software/general/software-general-reference_material-list/000002211) files
deconvoluted from their adapter information and seperated into 

## Method signature
```text
weave run [-h] 
    [-s/--seq_dir <sequencing directory>] 
    [-o/--output <output directory>] 
    [-d/--dry-run] 
    [-n/--noqc] 
    [-l/--local] 
    <run directory> [<run directory> ...]
```

## Example

### Setup
```bash 
# Step 1.) Grab an interactive node,
# do not run on head node!
sinteractive

# Step 2.) Follow install directions
source ~/.my_virtual_environment/bin/activate
```

### Dependencies

Ensure that snakemake and singularity are loaded and `$PATH` accessible.

If executing from biowulf cluster:

```bash
# Step 3.) module load snakemake and depdenencies 
module purge
module load singularity snakemake
```

If executing from BigSky cluster:

```bash
# Step 4.) spack load snakemake and depdenencies
source /data/openomics/bin/dependencies.sh
```

### Execution

```bash
# Step 4A.) Dry-run the weave pipeline
./weave run <run id> \
                  --output /data/$USER/output \
                  --dry-run

# Step 4B.) Run the weave pipeline
# The slurm mode will submit jobs to 
# the cluster. It is recommended running 
# the pipeline in this mode.
./weave run <run id> \
                  --output /data/$USER/output \
```

#### Run Identifiers (runid)

Run identifiers are strings that uniquely identify a particular sequencing run and are of the format:

`DATE<YYMMDD>_INSTRUMENTID_TIME<24hr>_FLOWCELLID`

## Arguments

### Required
Each of the following arguments are required. Failure to provide a required argument will result in a non-zero exit-code.

  `<run directory> [<run directory> ...]`  
> **Input runid or run directory.**  
> *type: strings(s)/path(s)*  
> 
> One or more IDs or directories can be provided and the pipeline will run them. 
> It is not necessary to specify server configuration information such as data parent directory, unless you
> on a non-standard cluster.
> 
> ***Example:*** `220729_NB551182_0219_AHGGJNBGXK`

---  
  `--output OUTPUT`
> **Path to the top-level output directory.**   
> *type: strings(s)/path(s)*  
>   
> This location is where the pipeline will create all of its output files. If the provided output directory does not exist, it will be created automatically.
> 
> ***Example:*** `--output /data/$USER/weave_out`

### Optional

Each of the following arguments are optional, and do not need to be provided. 

  `--dry-run`            
> **Dry run the pipeline.**  
> *type: boolean flag*
> 
> Displays what steps in the pipeline remain or will be run. Does not execute anything!
>
> ***Example:*** `--dry-run`

---  
  `--local`            
> **Execute locally instead of through a cluster executor**  
> *type: boolean flag*
> 
> This flag will trigger the workflow to run in the local terminal as a blocking process.
>
> ***Example:*** `--local`
