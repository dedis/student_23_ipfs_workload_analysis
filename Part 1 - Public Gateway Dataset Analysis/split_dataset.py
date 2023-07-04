import csv
from typing import Tuple
from tqdm import tqdm
import matplotlib.pyplot as plt

input_file: str = 'nginx-01-02-2021-bank2-sv15_encrypted.csv'
output_file1: str = 'nginx-Direct_requests_only.csv'
output_file2: str = 'nginx-HTTP_referrer_requests_only.csv'

def get_num_lines(input_file: str) -> int:
    """
    Get the number of lines in the input CSV file
    """
    with open(input_file) as csvfile:
        num_lines = sum(1 for line in csvfile)
    return num_lines

def process_rows(input_file: str, output_file1: str, output_file2: str, num_lines: int) -> Tuple[int, int]:
    """
    Process rows from the input CSV file and write them to two separate output files
    depending on the condition. Return the counts of rows written to each file.
    """
    count1 = 0
    count2 = 0

    with open(input_file, 'r', newline='') as infile:
        reader = csv.reader(infile, delimiter=',')
        next(reader) # Skip the header line
        with open(output_file1, 'w', newline='') as outfile1, open(output_file2, 'w', newline='') as outfile2:
            writer1 = csv.writer(outfile1, delimiter=',')
            writer2 = csv.writer(outfile2, delimiter=',')

            for row in tqdm(reader, desc="Processing rows", total=num_lines-1):
                if row[9] == '-':
                    writer1.writerow(row)
                    count1 += 1
                else:
                    writer2.writerow(row)
                    count2 += 1

    return count1, count2

def create_pie_chart(count1: int, count2: int) -> None:
    """
    Create a pie chart based on the given counts
    """
    # Create pie chart
    labels = ['directly', 'via third-party website ("HTTP referrer")']
    sizes = [count1, count2]
    colors = ['#ff9999', '#66b3ff']
    
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('How are requests generated in the IPFS Gateway?')
    plt.savefig('Gateway_request_source.png', bbox_inches='tight')

num_lines = get_num_lines(input_file)
count1, count2 = process_rows(input_file, output_file1, output_file2, num_lines)
create_pie_chart(count1, count2)
