import time
import argparse
import subprocess
import csv
from datetime import datetime, timedelta
from typing import List, Tuple

current_iteration: int = 0

languages: List[Tuple[str, int]] = [('en', 1), ('tr', 1), ('my', 1), ('ar', 1), ('zh', 1), ('uk', 1), ('ru', 1), ('fa', 1)]

wikipedia_file_suffix: str = '.wikipedia-on-ipfs.org_links_1_CID.csv'

def is_ipfs_daemon_running() -> bool:
    """
    Check if IPFS daemon is running.
    
    Returns:
    - True if IPFS daemon is running, False otherwise.
    """
    result = subprocess.run("ps -A -o pid,command | grep 'ipfs daemon' | grep -v grep", shell=True, text=True, capture_output=True)
    return result.returncode == 0

def start_ipfs_daemon() -> None:
    """
    Start the IPFS daemon.
    """
    try:
        subprocess.Popen("ipfs daemon", shell=True)
        print("IPFS daemon started.")
        time.sleep(15)
    except Exception as e:
        print("Failed to start IPFS daemon:", e)

def count_rows_in_csv(file_path: str) -> int:
    """
    Count the number of rows in a CSV file, excluding the header.
    
    Parameters:
    - file_path: Path to the CSV file.

    Returns:
    - An integer representing the number of rows in the CSV file.
    """
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        # Skip the header
        next(csvreader)
        row_count = sum(1 for row in csvreader)
    return row_count

def run_script(filename: str, sample_size: int, measurement_name: str, random_seed: int) -> subprocess.CompletedProcess:
    """
    Run a Python script with certain parameters.
    
    Parameters:
    - filename: The filename of the CSV file to be processed.
    - sample_size: The number of samples to be processed.
    - measurement_name: A name for the measurement, useful for distinguishing and/or continuing measurements.
    - random_seed: The seed for the random number generator.

    Returns:
    - A CompletedProcess instance, which represents the process that was run.
    """
    script_path = 'process_CID.py'
    result = subprocess.run(["python3", script_path, filename, str(sample_size), str(measurement_name), str(random_seed)], check=True)
    return result

def run_all_scripts(measurement_name: str, random_seed: int) -> None:
    """
    Run scripts for all languages in the list of languages.
    
    Parameters:
    - measurement_name: A name for the measurement, useful for distinguishing and/or continuing measurements.
    - random_seed: The seed for the random number generator.
    """
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

    sample_percentage: float = args.sample_percentage
    interval: int = args.interval
    measurement_name: str = args.measurement_name
    random_seed: int = args.random_seed

    for i in range(len(languages)):
        languages[i] = (languages[i][0], int(count_rows_in_csv(f"./links/{languages[i][0]}{wikipedia_file_suffix}") * sample_percentage))
    
    if not is_ipfs_daemon_running():
        print("IPFS daemon is not running. Starting it now...")
        start_ipfs_daemon()
    else:
        print("IPFS daemon is already running.")

    try:
        while True:
            start_time: float = time.time()
            run_all_scripts(measurement_name, int(random_seed + current_iteration))
            end_time: float = time.time()
            execution_time: float = end_time - start_time
            current_iteration += 1

            print(f"Iteration {current_iteration} took {execution_time/60:.2f} minutes.")
            remaining_time: float = interval - execution_time
            if remaining_time > 0:
                next_start_time: datetime = datetime.now() + timedelta(seconds=remaining_time)
                print(f"Next iteration will start at {next_start_time.strftime('%H:%M:%S')}")
                print(f"Next random seed is: {int(random_seed + current_iteration)}")
                time.sleep(remaining_time)
            else:
                print("Next iteration will start immediately.")
    except KeyboardInterrupt:
        print("Script execution stopped manually.")  
