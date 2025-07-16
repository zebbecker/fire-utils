import time
import os
import datetime as dt
import pandas as pd

"""
Downloads VIIRS active fire detections from FIRMS API every five minutes
and records the time that each observation first appears. 

Saves output to current working directory as csv. 
"""

MAP_KEY = "0e50658bd8e8ea368db7379b0be28630"
FIRMS_API = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"


def download_and_record_new_rows(sat, old_df):
    query = f"/VIIRS_{sat}_NRT/world/1/" + dt.datetime.now().strftime("%Y-%m-%d")
    url = FIRMS_API + MAP_KEY + query

    if not isinstance(old_df, pd.DataFrame):
        df = pd.read_csv(url)
        df["time_first_downloaded"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"{dt.datetime.now().strftime('%H:%M:%S')}: "
            f"{len(df)} rows downlinked from {sat}. Download complete."
        )
        return df

    try:
        new = pd.read_csv(url)
        print(
            f"{dt.datetime.now().strftime('%H:%M:%S')}: "
            f"{len(new)} rows downlinked from {sat}. Download complete."
        )
    except Exception as e:
        print(
            f"{dt.datetime.now.strftime('%H:%M:%S')}: "
            f"While downloading {sat} NRT, error {e}"
        )
        return old_df

    if not old_df.empty:
        merged = new.merge(old_df, how="left", indicator=True)
        new_rows = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
    else:
        new_rows = new

    new_rows["time_first_downloaded"] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return pd.concat([old_df, new_rows], ignore_index=True)


def main():
    if os.path.exists("snpp.csv"):
        snpp = pd.read_csv("snpp.csv")
    else:
        snpp = None

    if os.path.exists("noaa20.csv"):
        noaa20 = pd.read_csv("noaa20.csv")
    else:
        noaa20 = None

    if os.path.exists("noaa21.csv"):
        noaa21 = pd.read_csv("noaa21.csv")
    else:
        noaa21 = None

    while True:
        snpp = download_and_record_new_rows("SNPP", snpp)
        noaa20 = download_and_record_new_rows("NOAA20", noaa20)
        noaa21 = download_and_record_new_rows("NOAA21", noaa21)

        snpp.to_csv("snpp.csv")
        noaa20.to_csv("noaa20.csv")
        noaa21.to_csv("noaa21.csv")
        time.sleep(300)  # every five minutes


if __name__ == "__main__":
    main()
