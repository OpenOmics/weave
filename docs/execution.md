**weave** is capable of automatically distributing its pipeline jobs across a slurm cluster. The context for it's initial execution can be varied as well.

The context is also centrally related to the configuration and setup of a particular cluster. Right now weave is configured to work with NIH clusters **skyline**, **biowulf**, and **bigsky**.


Typical contexts of execution include:

# srun (real time execution) (non-interactive)

The **weave** pipeline can be triggered from a head node in a non-interactive fashion:

## Bigsky/Skyline

!!! Note
    Dependency files for skyline and bigsky differ
    Bigsky: `/gs1/RTS/OpenOmics/bin/dependencies.sh`
    Skyline: `/data/openomics/bin/dependencies.sh`

```bash
source ${dependencies}
srun --export=ALL "weave run [keyword args] ${run_id}"
```

!!! Note
    srun (by default)[https://slurm.schedmd.com/srun.html#OPT_export] exports all environmental variables from the executing environment and `--export=ALL` can be left off

## Biowulf

```bash
srun --export=ALL "module load snakemake singularity; weave run [keyword args] ${run_id}"
```

# srun (real time execution) (interactive)

## Bigsky/Skyline

!!! Note
    Dependency files for skyline and bigsky differ
    Bigsky: `/gs1/RTS/OpenOmics/bin/dependencies.sh`
    Skyline: `/data/openomics/bin/dependencies.sh`

```bash
> # <head node>
srun --pty bash
> # <compute node>
source ${dependencies}
weave run [keyword args] ${run_id}
```

## Biowulf

```bash 
> # <head node>
sinteractive
> # <compute node>
module purge
module load snakemake singularity
weave run [keyword args] ${run_id}
```

Biowulf uses environmental modules to control software. After executing the above you should see a message similar to:

> [+] Loading snakemake  7.XX.X on cnXXXX<br />
> [+] Loading singularity  4.X.X  on cnXXXX<br />

# sbatch (later time execution)

## Bigsky/Skyline

### sbatch tempalte
```bash title="<b>bigsky-skyline sbatch template</b>"
#!/bin/bash
#SBATCH --job-name=<job_name>
#SBATCH --export=ALL
#SBATCH --time=01-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem=8g
#SBATCH --output=<stdout_file>_%j.out
source ${dependencies}
weave run \
-s /sequencing/root/dir \
-o output_dir \
<run_id>
```

This above script can serve as a template to create an sbatch script for weave. Update the psuedo-variables in the script to suit your particular needs then execute using sbatch command:

```bash
sbatch weave_script.sbatch
```

## Biowulf

### sbatch tempalte
```bash title="<b>biowulf sbatch template</b>"
#!/bin/bash
#SBATCH --job-name=<job_name>
#SBATCH --export=ALL
#SBATCH --time=01-00:00:00
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem=8g
#SBATCH --output=<stdout_file>_%j.out
module purge
module load snakemake singularity
weave run \
-s /sequencing/root/dir \
-o output_dir \
<run_id>
```

Same sbatch execution as bigsky/skyline.

```bash
sbatch weave_script.sbatch
```