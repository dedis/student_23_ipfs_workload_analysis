from typing import Tuple, List, Dict
import csv
import os
import datetime
import re

wikipedia_file_suffix = '.wikipedia-on-ipfs.org_links_1_CID.csv'

# Languages and their associated colors for plotting
languages: List[Tuple[str, str, str]] = [('en', 'English', 'darkred'),
            ('ru', 'Russian', 'darkblue'),
            ('uk', 'Ukrainian', 'blue'),
            ('tr', 'Turkish', 'red'),
            ('ar', 'Arabic', 'yellow'),
            ('zh', 'Chinese', 'black'),
            ('my', 'Myanmar (Burmese)', 'teal'),
            ('fa', 'Persian (Farsi)', 'orange')]

def count_rows_in_csv(file_path: str) -> int:
    """
    Count the number of rows in a csv file.

    Args:
        file_path: The path to the csv file.

    Returns:
        The number of rows in the csv file.
    """
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Skip the header
        next(csvreader)
        row_count = sum(1 for row in csvreader)
    return row_count

def parse_timestamp(filename: str) -> datetime:
    """
    Extract timestamp from filename.

    Args:
        filename: The filename string.

    Returns:
        The timestamp extracted from the filename.
    """
    basename = os.path.basename(filename)
    timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", basename).group()
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")