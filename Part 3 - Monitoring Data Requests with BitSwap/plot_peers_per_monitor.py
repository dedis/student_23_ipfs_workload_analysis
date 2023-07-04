import datetime
import json
import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from typing import Dict, List, Set


# Function to get all JSON file names in a folder
def get_file_names(folder: str) -> List[str]:
    """Return all JSON file names in a specified folder."""
    return [f for f in os.listdir(folder) if f.endswith('.json')]

# Function to parse JSON data from a file
def parse_json_data(folder: str, file: str) -> Set[str]:
    """Parse JSON data from a specified file and return a set of peer ids with connectedness equals to 1."""
    with open(os.path.join(folder, file)) as json_file:
        data = json.load(json_file)
        return set([item['peer_id'] for item in data['result']['peer_metadata'] if item['connectedness'] == 1])

# Function to save data to disk
def save_data_to_disk(data: Set[str], filename: str) -> None:
    """Save the data to a specified file."""
    with open(filename, 'w') as json_file:
        json.dump(list(data), json_file)

# Folders
folder1: str = '/run/media/sumun/External SSD/EPFL/connected_peers/docker_compose_monitor_01'
folder2: str = '/run/media/sumun/External SSD/EPFL/connected_peers/docker_compose_monitor_02'

# Get file names
files1: List[str] = sorted(get_file_names(folder1))
files2: List[str] = sorted(get_file_names(folder2))

print(files1)
print(files2)

# Initialize dictionaries to store counts
intersect_counts: Dict[datetime.datetime, int] = {}
only_node1_counts: Dict[datetime.datetime, int] = {}
only_node2_counts: Dict[datetime.datetime, int] = {}

it = 0
# Iterate over each file
for file1, file2 in zip(files1, files2):
    # Parse timestamp from file name
    timestamp: datetime.datetime = datetime.datetime.strptime(file1.split('_UTC')[0], '%Y-%m-%d_%H-%M-%S')
    
    # Parse JSON data
    data1: Set[str] = parse_json_data(folder1, file1)
    data2: Set[str] = parse_json_data(folder2, file2)
    
    # Calculate and store counts
    intersect: Set[str] = data1.intersection(data2)
    only_node1: Set[str] = data1.difference(data2)
    only_node2: Set[str] = data2.difference(data1)

    intersect_counts[timestamp] = len(intersect)
    only_node1_counts[timestamp] = len(only_node1)
    only_node2_counts[timestamp] = len(only_node2)

# Convert dictionaries to pandas DataFrames
df_intersect = pd.DataFrame(list(intersect_counts.items()), columns=['Time', 'Count'])
df_only_node1 = pd.DataFrame(list(only_node1_counts.items()), columns=['Time', 'Count'])
df_only_node2 = pd.DataFrame(list(only_node2_counts.items()), columns=['Time', 'Count'])


# Plot counts over time
plt.figure(figsize=(10,6))
plt.plot(df_intersect['Time'], df_intersect['Count'], label='Peers connected to both nodes', color="purple")
plt.plot(df_only_node1['Time'], df_only_node1['Count'], label='Peers only connected to node 1', color="blue")
plt.plot(df_only_node2['Time'], df_only_node2['Count'], label='Peers only connected to node 2', color="red")

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y, %H:%M'))
plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility

plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin to prevent cut-off

plt.xlabel('Time')
plt.ylabel('Number of Peers')
plt.title('Number of Connected Peers Over Time')
plt.legend()
plt.savefig('peers_per_monitor.png')
# plt.show()
