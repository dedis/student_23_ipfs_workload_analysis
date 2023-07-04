import os
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

directory: str = '/home/sumun/repos/ipfs-tools-original/unify-bitswap-traces/csv'
filenames: List[str] = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv.gz')]

def ecdf(data: pd.Series) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute ECDF for a one-dimensional array of measurements.
    
    Parameters:
    - data: A pandas Series object that contains the measurements.

    Returns:
    - x: Sorted data.
    - y: The ECDF values.
    """
    n: int = len(data)
    x: np.ndarray = np.sort(data)
    y: np.ndarray = np.arange(1, n+1) / n
    return x, y

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

# Filter out rows where priority is 0
df = df[df['priority'] != 0]

# Calculate RRP and URP
RRP: pd.Series = df['cid'].value_counts()  # Total number of rows that contain a particular CID
URP: pd.Series = df.groupby('peer_id')['cid'].nunique()  # Number of rows with distinct peer_id that contain a particular CID

# Compute counts for RRP and URP
RRP_counts: pd.Series = RRP.value_counts().sort_index()
URP_counts: pd.Series = URP.value_counts().sort_index()

# Plot RRP
x_rrp, y_rrp = ecdf(RRP_counts)
fig, axs = plt.subplots(1, 2, figsize=(12,6))
axs[0].plot(x_rrp, y_rrp, linestyle='-', color='black')  # Use line plot
axs[0].set_xscale('log')  # Set x-axis to log scale
axs[0].set_xlabel('Number of Requests (RRP)')
axs[0].set_ylabel('ECDF')
axs[0].set_title('RRP Score')

# Plot URP
x_urp, y_urp = ecdf(URP_counts)
axs[1].plot(x_urp, y_urp, linestyle='-', color='black')  # Use line plot
axs[1].set_xscale('log')  # Set x-axis to log scale
axs[1].set_xlabel('Number of Unique Peers (URP)')
axs[1].set_ylabel('ECDF')
axs[1].set_title('URP Score')

fig.suptitle('CID popularity')  # Set the title for the whole plot

plt.tight_layout()

plt.savefig('CID_popularity_RRP_URP.png')

plt.show()
