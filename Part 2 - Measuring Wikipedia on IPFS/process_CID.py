from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple, Union
import csv
import datetime
import os
import random
import re
import subprocess
import sys
import time

from bs4 import BeautifulSoup
from tqdm import tqdm
import requests

# Get the file names and parameters from the command line arguments
input_filename: str = str(sys.argv[1])
sample_size: int = int(sys.argv[2])
measurement_name: str = str(sys.argv[3])
random_seed: int = int(sys.argv[4])
random.seed(random_seed)

now: datetime.datetime = datetime.datetime.now()
date_string: str = now.strftime('%Y-%m-%d_%H-%M-%S')

folder: str = f"./data/{input_filename[:4]}/{sample_size}_{measurement_name}"
folder_CID = os.path.join(folder, "CID")
folder_Providers = os.path.join(folder, "Providers")

# Make sure the necessary directories exist
os.makedirs(folder, exist_ok=True)
os.makedirs(folder_CID, exist_ok=True)
os.makedirs(folder_Providers, exist_ok=True)

output1_filename: str = f"{folder_CID}/{date_string}.csv"
output2_filename: str = f"{folder_Providers}/{date_string}.csv"

# Create a dictionary to keep track of the number of appearances of each provider ID
provider_counts: Dict[str, int] = defaultdict(int)

def get_provider_information(provider: str, max_attempts: int = 3) -> Tuple[bool, Optional[str]]:
    """
    Try to find the IP address of the provider using the `ipfs dht findpeer` command.
    Retry if the provider is not reachable, up to `max_attempts` times.

    Parameters:
    - provider: a string that represents the provider's ID.
    - max_attempts: the maximum number of attempts to reach the provider.

    Returns:
    - A tuple, where the first element is a boolean that represents whether the provider is reachable, 
      and the second element is the IP address of the provider if it is reachable, and `None` otherwise.
    """
    output = ''
    for attempt in range(max_attempts):
        sleep_time = random.uniform(0, 5)
        time.sleep(sleep_time)
        provider_reachable = False
        try:
            output = subprocess.check_output(f"ipfs dht findpeer {provider}", shell=True, timeout=15, stderr=subprocess.DEVNULL).decode()
            provider_reachable = True
        except subprocess.TimeoutExpired as e:
            if e.stdout is not None:
                print(e.stdout)
            provider_reachable = False
        except:
            provider_reachable = False

        if provider_reachable:
            for line in output.splitlines():
                match = re.match(r"/ip4/((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))/tcp", line)
                if match:
                    ip_address = match.group(1)
                    if ip_address not in ('127.0.0.1', '0.0.0.0'):
                        return True, ip_address

    print(provider + ' no suitable connection possible')
    print(output)
    return False, None

def process_row(row: Tuple[str, str], max_attempts: int = 2) -> List[Union[str, bool, int]]:
    """
    Process a single row from the input CSV file. This involves the following steps:
    - Check if the website is reachable.
    - Find the providers of the resolved CID using the `ipfs dht findprovs` command.
    - Count the number of providers and keep track of their appearances.

    Parameters:
    - row: a tuple that represents a single row from the input CSV file, containing the original link and the resolved CID.
    - max_attempts: the maximum number of attempts to reach the website and find the providers of the resolved CID.

    Returns:
    - A list that represents the processed row, which includes the original link, the resolved CID, a boolean that 
      indicates whether the website is reachable, the number of providers, a string that contains the list of providers, 
      and a flag that indicates whether there are providers in the IPFS network.
    """
    original_link, resolved_cid = row
    link = f'https://{original_link}'
    # print(original_link)
    website_reachable = False
    for attempt in range(max_attempts):
        if website_reachable == False:
            try:
                response = requests.get(link, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    pre_tag = soup.find('pre')
                    if pre_tag is None or not pre_tag.get_text().startswith('failed to resolve /ipns/'):
                        website_reachable = True
          
            except requests.exceptions.RequestException as e:
                # print(f'Weird error when accessing {link}...')
                print(f'RequestException: {e}')

    if not website_reachable:
        print(f'{link} does not load')

    for attempt in range(max_attempts):
        sleep_time = random.uniform(0, 5)
        time.sleep(sleep_time)
        try:
            result = subprocess.run(f"ipfs dht findprovs {resolved_cid}", shell=True, capture_output=True, text=True, timeout=15)
            output = result.stdout.strip().split("\n")
        except subprocess.TimeoutExpired as e:
            if e.stdout is not None:
                output = e.stdout.decode().strip().split("\n")
            else:
                continue
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}: {e.output}")
            print(f"Error on: ipfs dht findprovs {resolved_cid}")
            continue

        filtered_output = (item for item in output if item)  # Change to a generator expression
        if not filtered_output:
            continue

        providers = [p.split("/")[-1] for p in filtered_output]

        if len(providers) > 0:
            for p in providers:
                provider_counts[p] += 1
            
            return [original_link, resolved_cid, website_reachable, len(providers), ",".join(providers), 1]

    return [original_link, resolved_cid, website_reachable, 0, '', 0]

# At this point in the script, the input CSV file is opened and processed row by row in parallel.
# The processed rows are written to the output1 CSV file.
# The number of articles available in the IPFS network and the number of reachable articles are counted and printed.
with open(f"./links/{input_filename}", "r") as input_file, open(output1_filename, "w", newline="") as output1_file:
    # Set up the CSV reader and writer objects
    input_reader = csv.reader(input_file)
    input_rows = list(input_reader)[1:]
    
    num_total_rows = len(input_rows)
    if sample_size == 0:
        num_rows = num_total_rows
    else:
        num_rows = int(sample_size)
        input_rows = random.sample(input_rows, num_rows)


    output1_writer = csv.writer(output1_file)
    # Write the header row for output1.csv
    output1_writer.writerow(["Original Link", "Resolved CID", "Website available", "Number of Providers", "List of Providers"])

    articles_available_in_IPFS = 0
    reachable_articles = 0

    # Process CIDs in parallel
    with ThreadPoolExecutor(max_workers=min(32, num_rows)) as executor:
        progress_bar = tqdm(executor.map(process_row, input_rows, chunksize=max(1, num_rows // 32)), total=num_rows, file=sys.stdout)
        for row in progress_bar:
            articles_available_in_IPFS += row[-1]
            if row[2]:
                reachable_articles += 1
            output1_writer.writerow(row[:-1])

print(f"{articles_available_in_IPFS} out of {num_rows} articles had providers in IPFS...")
print(f"{reachable_articles} out of {num_rows} articles were reachable on the website...")

# At this point in the script, the output2 CSV file is created, and the provider information is processed in parallel.
# The provider information includes the provider ID, the number of appearances of the provider, 
# whether the provider is reachable, and the IP address of the provider.
with open(output2_filename, "w", newline="") as output2_file:
    # Set up the CSV writer object
    output2_writer = csv.writer(output2_file)
    # Write the header row for output2.csv
    output2_writer.writerow(["Provider ID", "Number of Appearances", "Reachable", "IP Address"])

    output2_rows = ''
    # Process provider information in parallel
    if len(provider_counts) > 0:
        with ThreadPoolExecutor(max_workers=min(16, len(provider_counts))) as executor:
            progress_bar = tqdm(executor.map(get_provider_information, provider_counts.keys(), chunksize=max(1, len(provider_counts) // 16)), total=len(provider_counts), file=sys.stdout)
            for (provider, count), (reachable, ip_address) in zip(provider_counts.items(), progress_bar):
                output2_row = [provider, count, reachable, ip_address]
                output2_writer.writerow(output2_row)