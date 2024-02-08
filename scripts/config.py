import re
import json
import traceback
import logging
from pathlib import Path
from os import access as check_access, R_OK
from os.path import expandvars, expanduser
from socket import gethostname
from uuid import uuid4
from collections import defaultdict


def get_current_server():
    """Return the current server name by looking at the hostname

    Returns:
        (str): one of `bigsky`, `biowulf`, or `locus`
    """
    hn = gethostname()
    # bigsky hostnames
    re_bigsky = (r"ai-rml.*\.niaid\.nih\.gov", "bigsky")

    # biowulf hostnames
    re_biowulf_head = (r"biowulf\.nih\.gov", "biowulf")
    re_biowulf_compute = (r"cn\d{4}", "biowulf")
    
    # skyline hostnames
    re_skyline_head = (r"ai-hpc(submit|n)(\d+)?", "skyline")
    re_skyline_compute = (r"ai-hpc(submit|n)(\d+)?", "skyline")

    host_profiles = [re_bigsky, re_biowulf_compute, re_biowulf_head, re_skyline_head, re_skyline_compute]

    host = None
    for pat, this_host in host_profiles:
        if re.match(pat, hn):
            host = this_host
            break
    if host is None:
        raise ValueError(f"Unknown host profile")
    return host


BIGSKY_QA, BIGSKY_DEV, BIGSKY_PROD = "rtblims-qa.niaid.nih.gov", "rtblims-dev.niaid.nih.gov", "rtblims.niaid.nih.gov"
BIGSKY_PATH = "Prod_Dup_20230509"


FRCE_PROD = "hgrepo.niaid.nih.gov",
FRCE_PATH = "COVID-19_Consortium"


# ~~~ labkey configurations ~~~ 
CONTEXT_PATH = "labkey"
LABKEY_CONFIGS = {
    "bigsky": {"domain": BIGSKY_DEV, "container_path": BIGSKY_PATH, "context_path": CONTEXT_PATH, "use_ssl": True},
    "frce": {"domain": FRCE_PROD, "container_path": FRCE_PATH, "context_path": CONTEXT_PATH, "use_ssl": True}
}


# ~~~ snakemake configurations ~~~ 
illumina_pipelines = defaultdict(lambda: Path(Path(__file__).parent.parent, "workflow", "Snakefile").resolve())
# can add support for NextSeq2k and bclconvert here
SNAKEFILE = {
    "Illumnia": illumina_pipelines
}


# ~~~ configuration helpers ~~~
remote_resource_confg = Path(Path(__file__).parent, '..', 'config', 'remote.json').absolute()


def get_resource_config():
    """Return a dictionary containing server specific references utilized in 
    the workflow for directories or reference files.

    Returns:
        (dict): return configuration key value pairs of current server::

            {
            "sif": "/server/location/to/sif/directory",
            "mounts": {
                "refence binding": {
                    "to": "/bind/to",
                    "from": "/bind/from",
                    "mode": "ro/rw"
                },
                ...
            }
    """
    resource_dir = Path(__file__, '..', '..', 'config').absolute()
    resource_json = Path(resource_dir, get_current_server() + '.json').resolve()

    if not resource_json.exists():
        return None

    return json.load(open(resource_json))


def base_config(keys=None, qc=True, slurm_id=None):
    base_keys = ('runs', 'run_ids', 'project', 'rnums', 'bcl_files', \
                'sample_sheet', 'samples', 'sids', 'out_to', 'demux_input_dir', \
                'bclconvert', 'demux_data')
    this_config = {k: [] for k in base_keys}
    this_config['resources'] = get_resource_config()
    this_config['runqc'] = qc
    this_config['use_scratch'] = True if slurm_id else False

    if keys:
        for elem_key in keys:
            this_config[elem_key] = []
    return this_config


def get_biowulf_seq_dirs():
    """Get a list of sequence directories, that have the required illumnia file artifacts:
    RTAComplete.txt - breadcrumb file created by bigsky transfer process and illumnia sequencing

    Returns:
        (list): list of `pathlib.Path`s of all sequencing directories on biowulf server
    """
    top_dir = Path("/data/RTB_GRS/SequencerRuns/")
    transfer_breadcrumb = "RTAComplete.txt"
    if not top_dir.exists():
        return None
    return [xx for x in top_dir.iterdir() if x.is_dir() for xx in x.iterdir() if xx.is_dir() and Path(xx, transfer_breadcrumb).exists()]


def get_bigsky_seq_dirs():
    """Get a list of sequence directories, that have the required illumnia file artifacts:
    RTAComplete.txt - breadcrumb file created by bigsky transfer process and illumnia sequencing

    Returns:
        (list): list of `pathlib.Path`s of all sequencing directories on bigsky server
    """
    top_dir = Path("/gs1/RTS/NextGen/SequencerRuns/")
    transfer_breadcrumb = "RTAComplete.txt"
    if not top_dir.exists():
        return None
    seq_dirs = []
    for this_dir in top_dir.iterdir():
        if not this_dir.is_dir(): continue
        for this_child_elem in this_dir.iterdir():
            try:
                elem_checks = [
                    this_child_elem.is_dir(), 
                    Path(this_child_elem, transfer_breadcrumb).exists(),
                    check_access(this_child_elem, R_OK)
                ]
            except (PermissionError, FileNotFoundError) as error:
                continue
            if all(elem_checks):
                seq_dirs.append(this_child_elem.absolute())
    return seq_dirs


def get_tmp_dir(host):
    TMP_CONFIGS = {
        'skyline': {'user': '/data/scratch/$USER/$SLURM_JOBID', 'global': '/data/scratch/$USER/' + str(uuid4())},
        'bigsky': {'user': '/gs1/Scratch/$USER/$SLURM_JOBID', 'global': '/gs1/Scratch/$USER/' + str(uuid4())},
        'biowulf': {'user': '/lscratch/$SLURM_JOBID', 'global': '/tmp/$USER/' + str(uuid4())}
    }

    this_tmp = TMP_CONFIGS[host]['user']

    # this directory, if it does not exist, 
    if Path(this_tmp).parents[0].exists():
        return this_tmp
    else:
        return TMP_CONFIGS[host]['global']


DIRECTORY_CONFIGS = {
    "bigsky": {
        "seqroot": "/gs1/RTS/NextGen/SequencerRuns/",
        "seq": get_bigsky_seq_dirs(),
        "profile": Path(Path(__file__).parent.parent, "utils", "profiles", "bigsky").resolve(),
    },
    "biowulf": {
        "seqroot": "/data/RTB_GRS/SequencerRuns/",
        "seq": get_biowulf_seq_dirs(),
        "profile": Path(Path(__file__).parent.parent, "utils", "profiles", "biowulf").resolve(),
    },
    "skyline": {
        "seqroot": "/data/rtb_grs/SequencerRuns/",
        "seq": get_bigsky_seq_dirs(),
        "profile": Path(Path(__file__).parent.parent, "utils", "profiles", "skyline").resolve(),
    }
}


GENOME_CONFIGS = {
    "biowulf": {
        "hg19": "/vf/users/OpenOmics/references/genomes/human/hg19/GRCh37.primary_assembly.genome.fa.gz",
        "grch37": "/vf/users/OpenOmics/references/genomes/human/GRCh37/GRCh37.primary_assembly.genome.fa.gz",
        "hg38": "/vf/users/OpenOmics/references/genomes/human/hg38/GRCh38.p14.genome.fa.gz",
        "grch38":  "/vf/users/OpenOmics/references/genomes/human/GRCh38/GRCh38.p14.genome.fa.gz",
        "mm9":  "/vf/users/OpenOmics/references/genomes/mouse/mm9/mm9.fa.gz",
        "grcm37":  "/vf/users/OpenOmics/references/genomes/mouse/GRCm37/mm9.fa.gz",
        "mm10":  "/vf/users/OpenOmics/references/genomes/mouse/mm10/GRCm38.p4.genome.fa.gz",
        "grcm38":  "/vf/users/OpenOmics/references/genomes/mouse/GRCm38/GRCm38.p4.genome.fa.gz",
        "mm39":  "/vf/users/OpenOmics/references/genomes/mouse/mm39/GRCm39.genome.fa.gz",
        "grcm39":  "/vf/users/OpenOmics/references/genomes/mouse/GRCm39/GRCm3s9.genome.fa.gz",
        "rhemac10": "/vf/users/OpenOmics/references/genomes/rhesus/rhe10/rheMac10.fa.gz",
        "mmul10": "/vf/users/OpenOmics/references/genomes/rhesus/mmul10/rheMac10.fa.gz",
        "agm": "/vf/users/OpenOmics/references/genomes/agm/1.1/GCF_000409795.2_Chlorocebus_sabeus_1.1_genomic.fna.gz",
        "mesaur": "/vf/users/OpenOmics/references/genomes/mesaur/2.0/GCF_017639785.1_BCM_Maur_2.0_genomic.fna.gz",
        "cynomac": "/vf/users/OpenOmics/references/genomes/cynomac/v2/GCF_012559485.2_MFA1912RKSv2_genomic.fna.gz",
    },
    "bigsky": {
        "hg19": "/gs1/RTS/OpenOmics/references/genomes/human/hg19/GRCh37.primary_assembly.genome.fa.gz",
        "grch37": "/gs1/RTS/OpenOmics/references/genomes/human/GRCh37/GRCh37.primary_assembly.genome.fa.gz",
        "hg38": "/gs1/RTS/OpenOmics/references/genomes/human/hg38/GRCh38.p14.genome.fa.gz",
        "grch38":  "/gs1/RTS/OpenOmics/references/genomes/human/GRCh38/GRCh38.p14.genome.fa.gz",
        "mm9":  "/gs1/RTS/OpenOmics/references/genomes/mouse/mm9/mm9.fa.gz",
        "grcm37":  "/gs1/RTS/OpenOmics/references/genomes/mouse/GRCm37/mm9.fa.gz",
        "mm10":  "/gs1/RTS/OpenOmics/references/genomes/mouse/mm10/GRCm38.p4.genome.fa.gz",
        "grcm38":  "/gs1/RTS/OpenOmics/references/genomes/mouse/GRCm38/GRCm38.p4.genome.fa.gz",
        "mm39":  "/gs1/RTS/OpenOmics/references/genomes/mouse/mm39/GRCm39.genome.fa.gz",
        "grcm39":  "/gs1/RTS/OpenOmics/references/genomes/mouse/GRCm39/GRCm39.genome.fa.gz",
        "rhemac10": "/gs1/RTS/OpenOmics/references/genomes/rhesus/rhe10/rheMac10.fa.gz",
        "mmul10": "/gs1/RTS/OpenOmics/references/genomes/rhesus/mmul10/rheMac10.fa.gz",
        "agm": "/gs1/RTS/OpenOmics/references/genomes/agm/1.1/GCF_000409795.2_Chlorocebus_sabeus_1.1_genomic.fna.gz",
        "mesaur": "/gs1/RTS/OpenOmics/references/genomes/mesaur/2.0/GCF_017639785.1_BCM_Maur_2.0_genomic.fna.gz",
        "cynomac": "/gs1/RTS/OpenOmics/references/genomes/cynomac/v2/GCF_012559485.2_MFA1912RKSv2_genomic.fna.gz",
    },
}