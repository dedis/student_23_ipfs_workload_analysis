import os
import csv
import re
from collections import defaultdict

def extract_cid(line: str) -> str:
    """
    Extracts the CID from the given log line.

    Args:
        line (str): A log line containing the CID.

    Returns:
        str: The extracted CID if found. Otherwise, None.
    """
    match = re.search(r'GET /ipfs/[a-zA-Z0-9]{44,62}', line)
    return match.group(0) if match else None

def process_directory(directory: str) -> dict:
    """
    Processes all CSV files in the given directory and extracts basic information from them.

    Args:
        directory (str): The directory containing the CSV files.

    Returns:
        dict: A dictionary mapping from filename to a dictionary of basic information.
    """
    result = defaultdict(list)

    for filename in os.listdir(directory):
        if filename.endswith('.csv') and filename.count('_') == 1:
            file_path = os.path.join(directory, filename)

            with open(file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                num_requests = 0
                num_user_agents = set()
                total_response_size = 0
                success_count = 0
                cache_hit_count = 0
                unique_cids = set()

                for row in csv_reader:
                    num_requests += 1
                    status_code = int(row[2])
                    total_response_size += int(row[3])
                    num_user_agents.add(row[10])
                    cid = extract_cid(row[1])
                    if cid:
                        unique_cids.add(cid)

                    if 200 <= status_code < 300:
                        success_count += 1
                    if 'HIT' in row[8]:
                        cache_hit_count += 1

                file_result = {
                    'num_requests': num_requests,
                    'num_user_agents': len(num_user_agents),
                    'num_CIDs': len(unique_cids),
                    'total_response_size': total_response_size,
                    'success_ratio': success_count / num_requests,
                    'cache_hit_ratio': cache_hit_count / num_requests
                }
                
                result[filename] = file_result

    return result

def save_results(results: dict, output_file: str) -> None:
    """
    Saves the processed results to an output file.

    Args:
        results (dict): The processed results.
        output_file (str): The output file path.
    """
    sorted_results = sorted(results.items(), key=lambda x: x[1]['num_requests'], reverse=True)

    with open(output_file, 'w') as f:
        for filename, result in sorted_results:
            f.write(f"=========================\n{filename}\n=========================\n")
            f.write(f"num_requests: {result['num_requests']}\n")
            f.write(f"num_user_agents: {result['num_user_agents']}\n")
            f.write(f"num_CIDs: {result['num_CIDs']}\n")
            f.write(f"total_response_size: {result['total_response_size']}\n")
            f.write(f"success_ratio: {result['success_ratio']:.2f}\n")
            f.write(f"cache_hit_ratio: {result['cache_hit_ratio']:.2f}\n\n")

directory = 'isolated_domains'
output_file = 'basic_info.txt'
results = process_directory(directory)
save_results(results, output_file)
