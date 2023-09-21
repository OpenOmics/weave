from pathlib import Path


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


DIRECTORY_CONFIGS = {
    'bigsky': {'seq': Path('/gs1/RTS/NextGen/SequencerRuns')}
}
