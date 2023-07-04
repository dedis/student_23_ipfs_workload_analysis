import os
import json
import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Function to get all JSON file names in a folder
def get_file_names(folder):
    return [f for f in os.listdir(folder) if f.endswith('.json')]

# Function to parse JSON data from a file
def parse_json_data(folder, file):
    with open(os.path.join(folder, file)) as json_file:
        data = json.load(json_file)
        return set([item['peer_id'] for item in data['result']['peer_metadata'] if item['connectedness'] == 1])


# Function to calculate IoU
def calculate_iou(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

# Folders
folder1 = '/run/media/sumun/External SSD/EPFL/connected_peers/docker_compose_monitor_01'
folder2 = '/run/media/sumun/External SSD/EPFL/connected_peers/docker_compose_monitor_02'

# Get file names
files1 = sorted(get_file_names(folder1))
files2 = sorted(get_file_names(folder2))

print(files1)
print(files2)

# Initialize dictionary to store IoU values
iou_values = {}

# Iterate over each file
for file1, file2 in zip(files1, files2):
    # Parse timestamp from file name
    timestamp = datetime.datetime.strptime(file1.split('_UTC')[0], '%Y-%m-%d_%H-%M-%S')
    
    # Parse JSON data
    data1 = parse_json_data(folder1, file1)
    data2 = parse_json_data(folder2, file2)
    
    # Calculate and store IoU
    iou_values[timestamp] = calculate_iou(data1, data2)

# Convert dictionary to pandas DataFrame
df = pd.DataFrame(list(iou_values.items()), columns=['Time', 'IoU'])

# Plot IoU over time
plt.figure(figsize=(10,6))
plt.plot(df['Time'], df['IoU'], label='IoU')
plt.xlabel('Time')
plt.ylabel('Intersection over Union')
plt.title('Intersection over Union (IoU) of peers')
plt.legend()
plt.show()
