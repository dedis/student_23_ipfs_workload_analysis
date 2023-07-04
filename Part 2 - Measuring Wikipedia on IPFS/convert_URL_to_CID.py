import sys
import subprocess
from tqdm import tqdm
import csv
from typing import List

# Get links file path from command line argument
links_file: str = sys.argv[1]

# Extract the input file name
input_file_name: str = links_file.split("/")[-1] # assuming links_file is a path, split it by '/' and take the last part

def resolve_links_and_write_to_file(links: List[str], output_file_name: str) -> None:
    """
    Resolve each link using IPFS and write the results to a CSV file.

    Args:
        links: A list of strings where each string is a link.
        output_file_name: The name of the output file.
    """
    with open(output_file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Original Link", "Resolved CID"])
        for link in tqdm(links, desc="Resolving links"):
            link = link.strip() # remove any whitespace characters
            try:
                command: str = f'ipfs resolve -r "/ipns/{link}"'
                output: str = subprocess.check_output(command, shell=True)
                output = output.decode().strip() # decode byte string to string and remove any whitespace characters
                output = output.replace('/ipfs/', '')
                writer.writerow([f"{link.replace('en.wikipedia-on-ipfs.org/wiki/', '')}", output])
            except Exception as e:
                print(f"Exception occurred: {e}", output)


if __name__ == "__main__":
    # Open links file and read links into a list
    with open(links_file, 'r') as file:
        links: List[str] = file.readlines()

    # Run ipfs resolve command on each link and save output to a file
    output_file_name: str = f"{input_file_name.replace('_links.txt', '')}_CID.csv"
    resolve_links_and_write_to_file(links, output_file_name)

    print(f"The resolved IPFS links have been saved to {output_file_name}.")
