import re
import json
from pathlib import Path
from os import access as check_access, R_OK
from socket import gethostname
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
    
    # locus hostnames
    re_locus_head = (r"ai\-submit\d{1}", "locus")
    re_locus_compute = (r"ai\-hpcn\d{3}", "locus")

    host_profiles = [re_bigsky, re_biowulf_compute, re_biowulf_head, re_locus_compute, re_locus_head]

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


def base_config(keys=None, qc=True):
    base_keys = ('runs', 'run_ids', 'project', 'rnums', 'bcl_files', \
                'sample_sheet', 'samples', 'sids', 'out_to', 'demux_input_dir')
    this_config = {k: [] for k in base_keys}
    this_config['resources'] = get_resource_config()
    this_config['runqc'] = qc

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
    }
}