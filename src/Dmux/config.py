from pathlib import Path
from os import access as check_access, R_OK


CONTEXT_PATH = 'labkey'


BIGSKY_QA, BIGSKY_DEV, BIGSKY_PROD = 'rtblims-qa.niaid.nih.gov', 'rtblims-dev.niaid.nih.gov', 'rtblims.niaid.nih.gov'
BIGSKY_PATH = 'Prod_Dup_20230509'


FRCE_PROD = 'hgrepo.niaid.nih.gov',
FRCE_PATH = 'COVID-19_Consortium'


LABKEY_CONFIGS = {
    'bigsky': {'domain': BIGSKY_DEV, 'container_path': BIGSKY_PATH, 'context_path': CONTEXT_PATH, 'use_ssl': True},
    'frce': {'domain': FRCE_PROD, 'container_path': FRCE_PATH, 'context_path': CONTEXT_PATH, 'use_ssl': True}
}


LABKEY_COLUMNS = {
    'bigsky': {
        BIGSKY_DEV: {'samplesheet': 'sampleSheet'},
        BIGSKY_QA: {'samplesheet': 'SampleSheet'}
    }
}

def get_biowulf_seq_dirs():
    top_dir = Path('/data/RTB_GRS/SequencerRuns/')
    transfer_breadcrumb = 'RTAComplete.txt'
    if not top_dir.exists():
        return None
    return [xx for x in top_dir.iterdir() if x.is_dir() for xx in x.iterdir() if xx.is_dir() and Path(xx, transfer_breadcrumb).exists()]


def get_bigsky_seq_dirs():
    top_dir = Path('/gs1/RTS/NextGen/SequencerRuns/')
    transfer_breadcrumb = 'RTAComplete.txt'
    if not top_dir.exists():
        return None
    return [xx for x in top_dir.iterdir() if x.is_dir() for xx in x.iterdir() if xx.is_dir() and Path(xx, transfer_breadcrumb).exists()]


def get_locus_seq_dirs():
    # TODO: locus
    top_dir = Path('/hpcdata/rtb_grs/SequencerRuns/')
    return None


DIRECTORY_CONFIGS = {
    'bigsky': {
        'seq': get_bigsky_seq_dirs(),
        'profile': Path(__file__, '..', '..', 'profiles').resolve()
    },
    'biowulf': {
        #'seq': get_biowulf_seq_dirs()
        'seq': [xx for x in Path('/data/OpenOmics/dev').iterdir() if x.is_dir() and check_access(x, R_OK) 
                for xx in x.iterdir() if xx.is_dir() and check_access(xx, R_OK) and Path(xx, 'RTAComplete.txt').exists()],
        'profile': Path(__file__, '..', '..', 'profiles').resolve()
    }
    # TODO: locus
}


SNAKEFILE = {
    'FASTQ': Path(__file__, '..', '..', 'workflow', 'FASTQ', 'Snakefile').resolve(),
    'NGS_QC': Path(__file__, '..', '..', 'workflow', 'NGS_QC', 'Snakefile').resolve(),
}

PROFILE = Path(__file__, '..', '..', 'profile').resolve()