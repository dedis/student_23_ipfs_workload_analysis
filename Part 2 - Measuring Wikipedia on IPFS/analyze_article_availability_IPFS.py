import os
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys
import csv
from matplotlib.dates import DateFormatter
from matplotlib.dates import DayLocator

sample_percentage = float(sys.argv[1])
measurement_name = str(sys.argv[2])

wikipedia_file_suffix = '.wikipedia-on-ipfs.org_links_1_CID.csv'

languages = [('en', 'English', 'darkred'),
            ('ru', 'Russian', 'darkblue'),
            ('uk', 'Ukrainian', 'blue'),
            ('tr', 'Turkish', 'red'),
            ('ar', 'Arabic', 'yellow'),
            ('zh', 'Chinese', 'black'),
            ('my', 'Myanmar (Burmese)', 'teal'),
            ('fa', 'Persian (Farsi)', 'orange')]


def count_rows_in_csv(file_path):
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # Skip the header
        next(csvreader)
        row_count = sum(1 for row in csvreader)
        # print(row_count)
    return row_count

# Function to parse timestamp from filename
def parse_timestamp(filename):
    basename = os.path.basename(filename)
    timestamp_str = re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", basename).group()
    # print(timestamp_str)
    return datetime.strptime(timestamp_str, "%Y-%m-%d_%H-%M-%S")

def evaluate_data(language, sample_size):
    # Read CSV files and store their data in a list of dictionaries
    data = []
    pattern = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_cleaned\.csv$"
    for file in glob.glob(f"./data/{language}/{sample_size}_{measurement_name}/CID/*.csv"):
        if re.match(pattern, os.path.basename(file)):
            df = pd.read_csv(file)
            timestamp = parse_timestamp(file)
            total = len(df)
            availables = len(df[df["Number of Providers"] > 0])

            if total == 0:
                continue

            availability_ratio = availables / total

            # Skip files with an availability ratio of 0
            if availability_ratio == 0:
                print(f'Skipped {file} due to availability_ratio of 0')
                continue
            data.append({"timestamp": timestamp, "availability_ratio": availability_ratio})

            if availability_ratio < 1:
                print(availability_ratio)

    data.sort(key=lambda x: x["timestamp"])
    timestamps = [entry["timestamp"] for entry in data]
    availability_ratio = [entry["availability_ratio"] for entry in data]

    # Return both raw data and moving average data
    return timestamps, availability_ratio

# Process and plot the data
sampled_data = {}
for lang, _, _ in languages:
    timestamps, availability_ratio = evaluate_data(lang, int(count_rows_in_csv('links/' + lang + str(wikipedia_file_suffix)) * sample_percentage))
    df = pd.DataFrame({'timestamp': timestamps, 'availability_ratio': availability_ratio})
    df.set_index('timestamp', inplace=True)

    # Calculate moving average
    df['moving_average'] = df['availability_ratio'].rolling(window=10).mean()
    sampled_data[lang] = df.reset_index()

# Plot the data
plt.figure(figsize=(12, 6))
for lang, label, color in languages:
    plt.plot(sampled_data[lang]['timestamp'], sampled_data[lang]['moving_average'], label=label, color=color)

plt.xlabel("Date")
plt.xticks(rotation=45)
plt.ylabel("Article Availability Ratio")
plt.title("Article Availability on IPFS")
plt.legend()

ax = plt.gca()  # Get the current axis
ax.xaxis.set_major_locator(DayLocator())  # Set ticks to start of each day
ax.xaxis.set_major_formatter(DateFormatter('%d.%m.%Y'))  # Display the date in 'dd.mm.yyyy' format

min_date = min([min(sampled_data[lang]['timestamp']) for lang, _, _ in languages])
max_date = max([max(sampled_data[lang]['timestamp']) for lang, _, _ in languages])

ax.set_xlim(min_date, max_date)

plt.tight_layout()
plt.savefig(f'figures/article_availability_ratio_{sample_percentage}_{measurement_name}_10.png')
