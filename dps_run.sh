#!/usr/bin/env -S bash --login
set -euo pipefail
# Entrypoint script used to trigger NIFC scraping job on DPS 

conda run --live-stream --name scraper python scrape_nifc_perims.py