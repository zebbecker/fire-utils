from fireatlas.FireRunDaskCoordinator import Run_local, Run_local_no_dask
from fireatlas.FireTypes import Region, TimeStep
from shapely.geometry import Point
import datetime as dt
import os
import subprocess
import cProfile
import traceback
import csv
from scalene import scalene_profiler

import pandas as pd
import geopandas as gpd


def run_feds_with_logging(region: Region, tst: TimeStep, ted: TimeStep):
    
    from fireatlas import settings 

    # start_timestamp = start_time.strftime("%Y%m%d_%H%M%S")

    os.makedirs("benchmark_logs", exist_ok=True)
    log_file = "./benchmark_logs/run_log.csv"

    run = 0
    
    if os.path.exists(log_file):
        with open(log_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if region[0] in row["region"]:
                    run += 1

    run_name = f"{region[0]}_run{run}"
    # profile_stats_filename = f"{run_name}.prof"
    profile_stats_filename = f"{run_name}.html"

    run_start_time = dt.datetime.now()

    log = {
        "run_name": run_name,
        "run_start_time": run_start_time.isoformat(),
        "run_end_time": "", 
        "duration_seconds": "",
        "region": region,
        "tst": tst,
        "ted": ted, 
        "git_branch": "", 
        "git_commit_hash": "", 
        "FIRE_SOURCE": settings.FIRE_SOURCE, 
        "N_DASK_WORKERS": settings.N_DASK_WORKERS,
        "FTYP_OPT": settings.FTYP_OPT, 
        "run_completed": False, 
        # "error": "",
        "profile_file": profile_stats_filename
    }

    try:
        log["git_branch"] = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"],stderr=subprocess.DEVNULL, text=True).strip()
        log["git_commit_hash"] = subprocess.check_output(["git", "rev-parse", "HEAD"],stderr=subprocess.DEVNULL, text=True).strip()
    except: 
        # if this doesnt work, whatever
        pass 

    # profiler = cProfile.Profile()

    try:
        # profiler.enable()
        scalene_profiler.start()
        print("Entering run local")
        _ = Run_local_no_dask(region, tst, ted)
        # _ = Run_local(region, tst, ted)
        print("Exiting run local")
        # profiler.disable()
        scalene_profiler.stop()
        log["run_completed"] = True
    except Exception as e:
        # profiler.disable()
        scalene_profiler.stop()
        # log["error"] = traceback.format_exc()
        print(e)
        pass
    
    run_end_time = dt.datetime.now()
    log["run_end_time"] = run_end_time.isoformat()
    log["duration_seconds"] = (run_end_time - run_start_time).total_seconds()

    # os.makedirs("benchmark_profiles", exist_ok=True)
    # profiler.dump_stats(f"./benchmark_profiles/{profile_stats_filename}")
    
    csv_file = "benchmark_logs/run_log.csv"
    exists = os.path.exists(csv_file)
    with open(csv_file, "a", newline="") as f:
        writer = csv.DictWriter(f, log.keys())
        if not exists:
            writer.writeheader()
        writer.writerow(log)
    
    print(f"[run_with_logging] Run logged to {csv_file}")
    print(f"[run_with_logging] Profile saved to {profile_stats_filename}")




def main():
    regions = ["Africa"]
    # regions = ["Africa",
    #            "Australia_New_Zealand",
    #            "Caribbean",
    #            "Central_Asia",
    #            "Europe_W_Siberia",
    #            "India", 
    #            "Japan_Far_East",
    #            "North_America",
    #            "SE_Asia", 
    #            "Seven_Seas", 
    #            "Siberia", 
    #            "South_America"]

    for r in regions:
        region = [r, r+".geojson"]
        tst = [2023, 1, 2, "AM"]
        ted = [2023, 1, 2, "PM"]
        run_feds_with_logging(region, tst, ted)

if __name__ == "__main__":
    main()