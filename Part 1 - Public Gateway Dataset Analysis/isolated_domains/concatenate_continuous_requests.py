import csv
import re
import sys
from datetime import datetime
from typing import List, Union

input_csv_file = str(sys.argv[1])
output_csv_file = str(sys.argv[1])[:-4] + '_concatenated.csv'

def extract_cid(line: str) -> str:
    """
    Extracts the Content Identifier (CID) from the provided HTTP request line.
    The CID is a unique identifier for a piece of content in the IPFS network.
    """
    pattern = r"GET /ipfs/([a-zA-Z0-9]+)"
    match = re.search(pattern, line)
    return match.group(1) if match else None

def compute_output_row(consecutive_rows: List[List[str]]) -> List[Union[int, float, str]]:
    """
    Computes the output row that will be written to the CSV file.
    It calculates several statistics based on the provided rows.
    """
    num_requests = len(consecutive_rows)
    server_timestamp_first, server_timestamp_last = consecutive_rows[0][0], consecutive_rows[-1][0]
    time_format = '%Y-%m-%dT%H:%M:%S%z'
    duration = (datetime.strptime(server_timestamp_last[1:-1], time_format) - datetime.strptime(server_timestamp_first[1:-1], time_format)).total_seconds()
    request_info_first, request_info_last = consecutive_rows[0][1], consecutive_rows[-1][1]
    successful_requests = sum(1 for row in consecutive_rows if row[2].startswith('2'))
    success_ratio = successful_requests / num_requests
    total_bytes_returned = sum(int(row[3]) for row in consecutive_rows if row[3] != '-')
    bytes_returned_average = total_bytes_returned / num_requests
    request_length_average = sum(int(row[4]) for row in consecutive_rows if row[4] != '-') / num_requests
    request_time_average = sum(float(row[5]) for row in consecutive_rows if row[5] != '-') / num_requests
    upstream_response_time_average = sum(float(row[6]) for row in consecutive_rows if row[6] != '-') / num_requests
    upstream_header_time_average = sum(float(row[7]) for row in consecutive_rows if row[7] != '-') / num_requests
    cache_hits = sum(1 for row in consecutive_rows if row[8] == 'HIT')
    cache_hit_ratio = cache_hits / num_requests
    http_referrer = consecutive_rows[0][9]
    user_agent = consecutive_rows[0][10]
    return [num_requests, server_timestamp_first, server_timestamp_last, duration, request_info_first, request_info_last, success_ratio, bytes_returned_average, total_bytes_returned, request_length_average, request_time_average, upstream_response_time_average, upstream_header_time_average, cache_hit_ratio, http_referrer, user_agent]

with open(input_csv_file, 'r') as infile, open(output_csv_file, 'w', newline='') as outfile:
    reader = csv.reader(infile, delimiter=',', quotechar='"')
    next(reader)  # Skip the header
    writer = csv.writer(outfile)
    writer.writerow(['num_requests', 'server_timestamp_first', 'server_timestamp_last', 'duration', 'HTTP_request_info_first', 'HTTP_request_info_last', 'Success_ratio', 'Bytes_returned_average', 'Total_bytes_returned', 'Request_length_average', 'Request_time_average', 'Upstream_response_time_average', 'Upstream_header_time_average', 'Cache_hit_ratio', 'HTTP_referrer', 'User_agent'])
    
    consecutive_rows = []
    for row in reader:
        if len(row) != 14:
            continue
        if consecutive_rows and extract_cid(consecutive_rows[-1][1]) != extract_cid(row[1]) and consecutive_rows[-1][9] != row[9] and consecutive_rows[-1][10] != row[10]:
            writer.writerow(compute_output_row(consecutive_rows))
            consecutive_rows = []
        consecutive_rows.append(row)
    if consecutive_rows:  # Don't forget the last batch of consecutive rows
        writer.writerow(compute_output_row(consecutive_rows))
