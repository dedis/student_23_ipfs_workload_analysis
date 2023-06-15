import sys
import subprocess
from tqdm import tqdm
import csv

# Get links file path from command line argument
links_file = sys.argv[1]

# Extract the input file name
input_file_name = links_file.split("/")[-1] # assuming links_file is a path, split it by '/' and take the last part

# Open links file and read links into a list
with open(links_file, 'r') as file:
    links = file.readlines()

# Run ipfs resolve command on each link and save output to a file
output_file_name = f"{input_file_name.replace('_links.txt', '')}_CID.csv"
with open(output_file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Original Link", "Resolved CID"])
    for link in tqdm(links, desc="Resolving links"):
        link = link.strip() # remove any whitespace characters
        try:
            command = f'ipfs resolve -r "/ipns/{link}"'
            output = subprocess.check_output(command, shell=True)
            output = output.decode().strip() # decode byte string to string and remove any whitespace characters
            output = output.replace('/ipfs/', '')
            writer.writerow([f"{link.replace('en.wikipedia-on-ipfs.org/wiki/', '')}", output])
        except:
            print(output)

print(f"The resolved IPFS links have been saved to {output_file_name}.")