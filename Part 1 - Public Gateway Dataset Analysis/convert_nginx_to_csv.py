import csv
import re
from typing import List, Optional, Union


# The file paths for the log, the generated CSV, and the file containing invalid entries
log_file = 'nginx-01-02-2021-bank2-sv15_encrypted.log'
csv_file = 'nginx-01-02-2021-bank2-sv15_encrypted.csv'
invalid_log = 'nginx-invalid-entries.csv'


def split_line(line: str) -> List[str]:
    """
    Split a log line into different parts, taking into account quoted strings.
    """
    parts = []
    current_part = ''
    inside_quotes = False

    for char in line:
        if char == '"':
            inside_quotes = not inside_quotes
        elif char == ' ' and not inside_quotes:
            parts.append(current_part.strip())
            current_part = ''
        else:
            current_part += char

    # Add the last part
    parts.append(current_part.strip())

    return parts


def find_cid(input_string: str) -> Optional[str]:
    """
    Find a CID in the given string. A CID is a string with alphanumerical characters and is between 44 and 62 characters long.
    """
    match = re.search(r'[a-zA-Z0-9]{44,62}', input_string)
    return match.group(0) if match else None


def is_integer(var: str) -> bool:
    """
    Check if a given string can be converted to an integer.
    """
    if var != '-':
        try:
            int(var)
        except ValueError:
            return False

    return True


def is_float(var: str) -> bool:
    """
    Check if a given string can be converted to a float.
    """
    if var != '-':
        try:
            float(var)
        except ValueError:
            return False
    
    return True
    

def is_row_valid(row: List[str]) -> bool:
    """
    Validate a row according to the specified conditions for each field.
    """
    # server_timestamp
    if len(row[0]) != 27:
        print(f'Invalid server_timestamp: {row[0]}')
        return False
    
    # HTTP_response_status_code
    if row[2] != '-' and not re.match(r'^\d{3}$', str(row[2])):
        print(f'Invalid HTTP_response_status_code: {row[2]}')
        return False

    # Bytes_returned
    if not is_integer(row[3]):
        print(f'Invalid Bytes_returned: {row[3]}')
        return False

    # Request_length
    if not is_integer(row[4]):
        print(f'Invalid Request_length: {row[4]}')
        return False

    # Request_time
    if not is_integer(row[5]) and not is_float(row[5]):
        print(f'Invalid Request_time: {row[5]}')
        return False

    # Upstream_response_time
    if not is_integer(row[6]) and not is_float(row[6]):
        print(f'Invalid Upstream_response_time: {row[6]}')
        return False

    # Upstream_header_time
    if not is_integer(row[7]) and not is_float(row[7]):
        print(f'Invalid Upstream_header_time: {row[7]}')
        return False

    # Cache_hit_miss
    if row[8] != '-' and row[8] != 'HIT' and row[8] != 'MISS' and row[8] != 'EXPIRED':
        print(f'Invalid Cache_hit_miss: {row[8]}')
        return False

    # User_agent
    if len(row[10]) == 0 or not row[10][0].isalpha():
        return False

    return True


# Process log file
with open(log_file, 'r') as logf, open(csv_file, 'w', newline='') as csvf, open(invalid_log, 'w', newline='') as inv_log:
    log_lines = logf.readlines()
    csv_writer = csv.writer(csvf)
    invalid_writer = csv.writer(inv_log)

    # Write headers
    headers = ['server_timestamp', 'HTTP_request_info', 'HTTP_response_status_code', 'Bytes_returned',
                'Request_length', 'Request_time', 'Upstream_response_time', 'Upstream_header_time', 'Cache_hit_miss',
                'HTTP_referrer', 'User_agent', 'Server_name', 'HTTP_host', 'HTTP_schema']
    csv_writer.writerow(headers)

    for line in log_lines:
        row = split_line(line)
        del row[0:3]  # Remove the first, second and third columns

        if row[1].startswith("GET "):
            cid = find_cid(row[1])
            if cid:
                csv_writer.writerow(row)
            else:
                cid = find_cid(row[12])
                if not cid:
                    cid = find_cid(row[9])

                if cid:
                    row[1] = f"GET /ipfs/{cid}" + row[1][4:]  # Remove the first four characters and prepend the new string
                    if len(row) == len(headers) and is_row_valid(row):
                        csv_writer.writerow(row)
                    else:
                        invalid_writer.writerow(row)
                else:
                    invalid_writer.writerow(row)
