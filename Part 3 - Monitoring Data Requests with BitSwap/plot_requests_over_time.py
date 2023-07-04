import os
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import pandas as pd
import seaborn as sns
from tqdm import tqdm
from typing import List

directory: str = '/home/sumun/repos/ipfs-tools-original/unify-bitswap-traces/csv'
# filenames: List[str] = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv.gz')][:11]
filenames: List[str] = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv.gz')]

# Load gateway peers
with open('gateway_peers.txt', 'r') as file:
    gateway_peers: List[str] = file.read().splitlines()

# Load and concatenate the csv.gz files
df_list: List[pd.DataFrame] = []
for filename in tqdm(filenames, desc="Processing files"):
    try:
        df_list.append(pd.read_csv(filename, compression='gzip'))
    except EOFError:
        print(f"Warning: {filename} ended before the end-of-stream marker was reached. It has been skipped.")
df: pd.DataFrame = pd.concat(df_list, ignore_index=True)

# Combine timestamp_seconds and timestamp_subsec_milliseconds
df['timestamp'] = df['timestamp_seconds'] + df['timestamp_subsec_milliseconds']*1e-9

# Keep only rows with unique combinations of timestamp, peer_id, and cid
df = df.drop_duplicates(subset=['timestamp', 'peer_id', 'cid'])

# Filter rows where priority is not 0
df = df[df['priority'] != 0]

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Generate counts per minute
df_total: pd.Series = df['timestamp'].value_counts().sort_index().resample('1T').sum()
df_gateways: pd.Series = df[df['peer_id'].isin(gateway_peers)]['timestamp'].value_counts().sort_index().resample('1T').sum()
df_normal: pd.Series = df[~df['peer_id'].isin(gateway_peers)]['timestamp'].value_counts().sort_index().resample('1T').sum()

# Generate plot
plt.figure(figsize=(12, 6))
sns.lineplot(data=df_total, label='Total')
sns.lineplot(data=df_gateways, label='Gateways')
sns.lineplot(data=df_normal, label='Normal Peers')

plt.xlabel('Time')
plt.ylabel('Number of BitSwap Messages')

# Y-axis formatting
y_format = FuncFormatter(lambda x, p: format(int(x), ',').replace(",", "'"))
plt.gca().yaxis.set_major_formatter(y_format)

plt.title('BitSwap Messages Received per Minute')

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y, %H:%M'))
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))  # to get a tick every 5 minutes

plt.xticks(rotation=45)  # Rotate x-axis labels for better visibility
plt.legend()

plt.subplots_adjust(bottom=0.2)  # Adjust bottom margin to prevent cut-off

plt.savefig('requests_over_time.png')
plt.show()
