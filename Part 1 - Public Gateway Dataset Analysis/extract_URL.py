import csv
from urllib.parse import urlparse
from collections import Counter
from tqdm import tqdm
from typing import List, Tuple

def count_lines(file_path: str) -> int:
    """
    Count the number of lines in a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        int: Number of lines in the file.
    """
    with open(file_path) as csvfile:
        return sum(1 for line in csvfile)

def extract_base_urls(file_path: str, num_lines: int) -> List[str]:
    """
    Extract base URLs from the 11th column of a CSV file.

    Args:
        file_path (str): Path to the CSV file.
        num_lines (int): Number of lines in the CSV file.

    Returns:
        List[str]: List of base URLs.
    """
    with open(file_path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=',')
        base_urls = []

        print("Processing input CSV file...")
        for row in tqdm(csv_reader, total=num_lines):
            url = row[9]
            parsed_url = urlparse(url)
            domain = parsed_url.netloc

            # Remove 'www.' from the domain if present
            if domain.startswith('www.'):
                domain = domain[4:]

            base_url = f"{parsed_url.scheme}://{domain}/"
            base_urls.append(base_url)
        
    return base_urls

def count_and_sort_urls(base_urls: List[str]) -> List[Tuple[str, int]]:
    """
    Count the occurrences of unique base URLs and sort them in descending order.

    Args:
        base_urls (List[str]): List of base URLs.

    Returns:
        List[Tuple[str, int]]: List of tuples where each tuple contains a base URL and its count.
    """
    base_url_counts = Counter(base_urls)
    return sorted(base_url_counts.items(), key=lambda x: x[1], reverse=True)

def write_to_csv(file_path: str, data: List[Tuple[str, int]]) -> None:
    """
    Write the unique base URLs and their occurrences to a new CSV file.

    Args:
        file_path (str): Path to the CSV file.
        data (List[Tuple[str, int]]): List of tuples where each tuple contains a base URL and its count.
    """
    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Base URL', 'Occurrences', 'Website Type'])

        for base_url, count in data:
            csv_writer.writerow([base_url, count, 'Unknown'])

    print(f"Results written to {file_path}")


input_csv_path = 'nginx-HTTP_referrer_requests_only_sorted.csv'
output_csv_path = 'extracted_URLs.csv'

num_lines = count_lines(input_csv_path)
base_urls = extract_base_urls(input_csv_path, num_lines)
sorted_base_url_counts = count_and_sort_urls(base_urls)
write_to_csv(output_csv_path, sorted_base_url_counts)
