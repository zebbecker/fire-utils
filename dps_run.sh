#!/usr/bin/env -S bash --login
set -euo pipefail
# Entrypoint script used to trigger NIFC scraping job on DPS 

basedir=$( cd "$(dirname "$0")"; pwd -P )
echo "Basedir: $basedir"
echo "Initial working directory: $(pwd -P)"
echo "conda: $(which conda)"
echo "Python: $(which python)"

pushd "$basedir"
echo "Running in directory: $(pwd -P)"

conda run --live-stream --name scraper python scrape_nifc_perims.py