#!/bin/bash --login
# The --login ensures the bash configuration is loaded, enabling Conda.

# Enable strict mode.
set -euo pipefail
# Temporarily disable strict mode and activate conda:
set +euo pipefail

conda init bash
source ~/.bashrc
conda activate ngsqc

# Re-enable strict mode:
set -euo pipefail
exec "$@"
