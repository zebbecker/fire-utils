"""
Quick script to scrape full set of current US fire perimeters from NIFC's
WFIGS's service and save them in the current working directory.

Run with inline dependencies: uv run scrape_nifc_perims.py
"""

# /// script
# dependencies = [
#   "geopandas",
#   "pyarrow",
#   "s3fs",
# ]
# ///
import s3fs
import datetime as dt
import geopandas as gpd
from pathlib import Path

query_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H%M")

attempts = 0
max_attempts = 3
while attempts <= max_attempts:
    try:
        # Download as geojson, read into gdf
        nifc_perimeters = gpd.read_file(
            "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/WFIGS_Interagency_Perimeters_Current/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson"
        )
        break
    except Exception as e:
        print(f"Attempt {attempts} resulted in error: {e}")
        attempts += 1
        if attempts > max_attempts:
            raise e

# add query time column
nifc_perimeters["query_time_utc"] = query_time

# save locally, then copy to s3
attempt = 0
max_attempts = 5

local_path = Path(".") / f"nifc_active_perimeter_query_{query_time}.parquet"
s3_path = f"s3://maap-ops-workspace/shared/gsfc_landslides/NIFC_Stored_Perimeters/nifc_active_perimeter_query_{query_time}.parquet"

nifc_perimeters.to_parquet(local_path)

fs = s3fs.S3FileSystem()
while attempt < max_attempts:
    try:
        fs.put_file(local_path, s3_path)

        print(f"Successfully saved {query_time}")
        break

    except Exception as e:
        attempt += 1
        print(
            f"Error occurred for saving {query_time} (attempt {attempt}/{max_attempts}): {e}"
        )
