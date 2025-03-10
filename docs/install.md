**weave** is a stand alone python script that triggers execution of containerized subjobs defined in the workflow. **weave** does require a few dependencies currently, with plans to dwindle these requirements in the future.


# Setup

!!! Warning

    All requirements should be installed to a python virtual environment and not to the system python

```bash
# clone repo
git clone https://github.com/OpenOmics/weave.git
cd weave
# create virtual environment
python -m venv ~/.my_venv
# activate environment
source ~/.my_venv/bin/activate
pip install -r requirements.txt 
```

## Snakemake & singularity

!!! Note

    Additional requirements beyond those listed in `requirements.txt` are the `Snakemake` python package and the `singularity` containerization software

### On NIH servers

```bash title="<b>Biowulf server</b>"
module purge
module load snakemake singularity`
```

Biowulf uses environmental modules to control software. After executing the above you should see a message similar to:

> [+] Loading snakemake  7.XX.X on cnXXXX<br />
> [+] Loading singularity  4.X.X  on cnXXXX

```bash title="<b>Bigsky</b>"
source /data/openomics/bin/dependencies.sh`
```

Bigsky uses spack to load modules so a consolidated conda environment with snakemake is activated:

```bash title="dependencies.sh"
if [ ! -x "$(command -v "snakemake")" ]; then
    source /gs1/apps/user/rmlspack/share/spack/setup-env.sh
    export PS1="${PS1:-}"
    spack load -r miniconda3@4.11.0/y4vyh4u
    source activate snakemake7-19-1
fi
# Add this folder to $PATH
export PATH="/data/openomics/bin:${PATH}"
# Add different pipelines to $PATH
export PATH="/data/openomics/prod/rna-seek/latest:${PATH}"
export PATH="/data/openomics/prod/metavirs/latest:${PATH}"
```

While, singularity is installed to the **BigSky** system and available upon login.

### Outside NIH servers

Please follow the relevent instructions on the related package(s): [Snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html) and [singularity](https://docs.sylabs.io/guides/3.5/user-guide/quick_start.html#quick-installation-steps)

# Quickstart

After installing all the dependencies you then test the workflow functionality using a the dry run switch in the **weave** frontend.

```bash
# after clone, dependencies, and installation
cd weave # git repository root
./weave run \
-s .tests/illumnia_demux \ 
-o .tests/illumnia_demux/dry_run_out \
--local --dry-run /opt2/.tests/illumnia_demux
```