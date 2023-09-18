CONTEXT_PATH = 'labkey'

BIGSKY_QA, BIGSKY_DEV, BIGSKY_PROD = 'rtblims-qa.niaid.nih.gov', 'rtblims-dev.niaid.nih.gov', 'rtblims.niaid.nih.gov'
BIGSKY_PROJECT = 'Prod_Dup_20230714'

FRCE_PROD = 'hgrepo.niaid.nih.gov',
FRCE_PROJECT = 'COVID-19_Consortium'

LABKEY_CONFIGS = {
    'bigsky': {'domain': BIGSKY_QA, 'container_path': BIGSKY_PROJECT, 'context_path': CONTEXT_PATH, 'use_ssl': True},
    'frce': {'domain': FRCE_PROD, 'container_path': FRCE_PROJECT, 'context_path': CONTEXT_PATH, 'use_ssl': True}
}
