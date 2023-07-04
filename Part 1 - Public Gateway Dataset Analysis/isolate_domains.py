import csv
import os
from typing import Dict, List, Tuple

def normalize_url(url: str) -> str:
    """
    Remove 'www.' from the URL if it exists.

    Args:
        url (str): Input URL string.
    
    Returns:
        str: Normalized URL string.
    """
    return url.replace("www.", "")

def read_csv(file_path: str, skip_header: bool = False) -> List[List[str]]:
    """
    Read CSV file and return data.

    Args:
        file_path (str): CSV file path.
        skip_header (bool, optional): Whether to skip header. Defaults to False.

    Returns:
        List[List[str]]: List of rows with each row as a list of columns.
    """
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        if skip_header:
            next(reader)  # Skip header
        data = [row for row in reader]
    return data

def write_to_csv(file_writers: Dict[str, csv.writer], data1: List[List[str]], data2: List[List[str]]) -> Dict[str, csv.writer]:
    """
    Write rows from data1 to corresponding files based on URLs found in data2.

    Args:
        file_writers (Dict[str, csv.writer]): Dictionary storing file writers for each URL.
        data1 (List[List[str]]): List of rows from first CSV file.
        data2 (List[List[str]]): List of rows from second CSV file.

    Returns:
        Dict[str, csv.writer]: Updated dictionary of file writers.
    """
    for row1 in data1:
        url = row1[9]  # Get the 10th column

        # Check if the URL is in the second CSV file
        for row2 in data2:
            normalized_url1 = normalize_url(row2[0])
            normalized_url2 = normalize_url(url)
            if normalized_url1 in normalized_url2:
                # If the URL is found, check if we already have a file writer for it
                if row2[0] not in file_writers:
                    # If not, create a new file writer
                    output_file_name = f'{row2[0].replace("://", "_")[:-1]}.csv'
                    output_file_path = os.path.join(output_dir, output_file_name)
                    output_file = open(output_file_path, 'w', newline='')
                    file_writers[row2[0]] = csv.writer(output_file)

                # Write the row to the corresponding output file
                file_writers[row2[0]].writerow(row1)
                break
    return file_writers

sorted_csv = 'nginx-HTTP_referrer_requests_only_sorted.csv'
domains_csv = 'extracted_URLs.csv'

output_dir = 'isolated_domains'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

data1 = read_csv(sorted_csv)
data2 = read_csv(domains_csv, skip_header=True)[:12]  # Get first 12 rows

file_writers: Dict[str, csv.writer] = {}
file_writers = write_to_csv(file_writers, data1, data2)

for output_file in file_writers.values():
    output_file.writerows([])