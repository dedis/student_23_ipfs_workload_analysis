import time
import argparse
import subprocess
import csv
from datetime import datetime, timedelta

current_iteration = 0

languages = [('en', 1), ('tr', 1), ('my', 1), ('ar', 1), ('zh', 1), ('uk', 1), ('ru', 1), ('fa', 1)]

wikipedia_file_suffix = '.wikipedia-on-ipfs.org_links_1_CID.csv'

def is_ipfs_daemon_running():
    result = subprocess.run("ps -A -o pid,command | grep 'ipfs daemon' | grep -v grep", shell=True, text=True, capture_output=True)
    return result.returncode == 0

def start_ipfs_daemon():
    try:
        subprocess.Popen("ipfs daemon", shell=True)
        print("IPFS daemon started.")
        time.sleep(15)
    except Exception as e:
        print("Failed to start IPFS daemon:", e)

def count_rows_in_csv(file_path):
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Skip the header
        next(csvreader)
        row_count = sum(1 for row in csvreader)
    return row_count

def run_script(filename, sample_size, measurement_name, random_seed):
    script_path = 'process_CID.py'
    result = subprocess.run(["python3", script_path, filename, str(sample_size), str(measurement_name), str(random_seed)], check=True)
    return result

def run_all_scripts(measurement_name, random_seed):
    for i in range(len(languages)):
        print('[MAIN SCRIPT] Processing language ' + str(languages[i][0]) + ' ...')
        run_script('./' + str(languages[i][0]) + str(wikipedia_file_suffix), int(languages[i][1]), measurement_name, int(random_seed))

        # Repeat measurement if IPFS daemon crashed
        while not is_ipfs_daemon_running():
            print("IPFS daemon has crashed. Restarting it now...")
            start_ipfs_daemon()
            print(f"Re-running script for language {languages[i][0]} due to IPFS daemon crash...")
            run_script('./' + str(languages[i][0]) + str(wikipedia_file_suffix), int(languages[i][1]), measurement_name, int(random_seed))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a script at fixed time intervals.")
    parser.add_argument("sample_percentage", type=float, help="Percentage of articles to sample per language (0.xx).")
    parser.add_argument("interval", type=int, help="Interval in seconds between script runs.")
    parser.add_argument("measurement_name", type=str, help="Name of the measurement. Useful for distinguishing and/or continuing measurements.")
    parser.add_argument("random_seed", type=int, nargs="?", default=42, help="Optional random seed to start. Default is 42.")

    args = parser.parse_args()

    sample_percentage = args.sample_percentage
    interval = args.interval
    measurement_name = args.measurement_name
    random_seed = args.random_seed

    for i in range(len(languages)):
        languages[i] = (languages[i][0], int(count_rows_in_csv(f"./links/{languages[i][0]}{wikipedia_file_suffix}") * sample_percentage))
    
    if not is_ipfs_daemon_running():
        print("IPFS daemon is not running. Starting it now...")
        start_ipfs_daemon()
    else:
        print("IPFS daemon is already running.")

    try:
        while True:
            start_time = time.time()
            run_all_scripts(measurement_name, int(random_seed + current_iteration))
            end_time = time.time()
            execution_time = end_time - start_time
            current_iteration += 1

            print(f"Iteration {current_iteration} took {execution_time/60:.2f} minutes.")
            remaining_time = interval - execution_time
            if remaining_time > 0:
                next_start_time = datetime.now() + timedelta(seconds=remaining_time)
                # print(f"Waiting for {remaining_time/60:.2f} minutes before running the script again...")
                # print(f"Next iteration will start at {next_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Next iteration will start at {next_start_time.strftime('%H:%M:%S')}")
                print(f"Next random seed is: {int(random_seed + current_iteration)}")
                time.sleep(remaining_time)
            else:
                print("Next iteration will start immediately.")
    except KeyboardInterrupt:
        print("Script execution stopped manually.")
                    
