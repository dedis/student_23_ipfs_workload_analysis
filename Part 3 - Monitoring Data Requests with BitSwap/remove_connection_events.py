import os
import gzip
import json
import multiprocessing
from typing import List

source_dir: str = "/run/media/sumun/External SSD/EPFL/traces/docker_compose_monitor_01/sunday/"
destination_dir: str = "/run/media/sumun/External SSD/EPFL/traces/docker_compose_monitor_01/bitswap_messages/"

# Ensure destination directory exists
os.makedirs(destination_dir, exist_ok=True)

def process_file(filename: str) -> None:
    """
    Function to process each file. It filters out lines containing 'connection_event'
    and writes the remaining lines to the destination file.

    Parameters:
    filename (str): The name of the file to process.
    """
    source_file_path: str = os.path.join(source_dir, filename)
    destination_file_path: str = os.path.join(destination_dir, filename)

    # Skip this file if it has been processed already
    if os.path.exists(destination_file_path):
        print(f"Skipping: {filename} (already processed)")
        return

    print(f"Processing: {filename}")

    # Open the source and destination files
    try:
        with gzip.open(source_file_path, 'rt') as source_file, gzip.open(destination_file_path, 'wt') as dest_file:
            # Parse each line in the source file
            for line in source_file:
                # Parse the line as a JSON object
                obj = json.loads(line)

                # If 'connection_event' is not in the object, write it to the destination file
                if 'connection_event' not in obj:
                    dest_file.write(json.dumps(obj) + '\n')
    except EOFError:
        print(f"Skipping: {filename} (corrupted or incomplete file)")

# Get list of all .json.gz files in the source directory
filenames: List[str] = [filename for filename in os.listdir(source_dir) if filename.endswith(".json.gz")]

# Create a pool of workers
with multiprocessing.Pool(8) as pool:
    pool.map(process_file, filenames)
