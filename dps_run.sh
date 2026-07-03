#!/usr/bin/env -S bash --login
set -euo pipefail
# Entrypoint script used to trigger NIFC scraping job on DPS 

pwd
ls
ls fire-utils/
conda run --live-stream --name scraper python scrape_nifc_perims.py