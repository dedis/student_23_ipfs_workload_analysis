import os
import glob
import re
import pandas as pd
from datetime import datetime
import sys
from typing import Tuple, List, Dict, Union
from helpers import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker
from matplotlib.dates import DateFormatter
from matplotlib.dates import DayLocator


# Arguments passed via command line 
sample_percentage: float = float(sys.argv[1])
measurement_name: str = str(sys.argv[2])

def evaluate_data(language: str, sample_size: int) -> Tuple[List[datetime], List[float]]:
    """
    Read data from CSV files and evaluate.

    Args:
        language: The language code string.
        sample_size: The sample size to be considered.

    Returns:
        Two lists - list of timestamps and corresponding reachability averages.
    """
    # Read CSV files and store their data in a list of dictionaries
    data: List[Dict[str, Union[datetime, int]]] = []
    pattern: str = r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.csv$"
    for file in glob.glob(f"./data/{language}/{sample_size}_{measurement_name}/Providers/*.csv"):
        if re.match(pattern, os.path.basename(file)):
            df = pd.read_csv(file)
            timestamp = parse_timestamp(file)
            total = len(df)
            reachable = len(df[df["Reachable"] == True])
            not_reachable = total - reachable
            
            if reachable != 0:
                data.append({"timestamp": timestamp, "total": total, "reachable": reachable, "not_reachable": not_reachable})

    data.sort(key=lambda x: x["timestamp"])
    timestamps = [entry["timestamp"] for entry in data]
    reachables = [entry["reachable"] for entry in data]

    # Compute moving averages for the 'reachables'
    reachables_df = pd.DataFrame(reachables)
    reachables_avg = reachables_df.rolling(window=10).mean().values.flatten().tolist()

    return timestamps, reachables_avg

full_data = {}
sampled_data = {}
for lang, _, _ in languages:
    full_data[lang] = count_rows_in_csv('links/' + lang + str(wikipedia_file_suffix))
    sampled_data[lang] = evaluate_data(lang, int(count_rows_in_csv('links/' + lang + str(wikipedia_file_suffix)) * sample_percentage))

sorted_languages = sorted(languages, key=lambda x: full_data[x[0]], reverse=True)
max_label_width = max([len(f"{full_data[lang],}") for lang, _, _ in sorted_languages])

fig, ax = plt.subplots(figsize=(10 + max_label_width * 0.6, 8))
for i, (lang, _, color) in enumerate(sorted_languages):
    count = full_data[lang]
    ax.barh(i, count, color=color, alpha=0.7)
    ax.text(count + 10, i, f"{count:,}", ha='left', va='center', fontsize=12)
ax.set_yticks(range(len(sorted_languages)))
ax.set_yticklabels([name for _, name, _ in sorted_languages])
ax.invert_yaxis()
ax.set_xlabel('Number of Articles')
ax.set_title('Wikipedia Articles per Language')
ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
plt.subplots_adjust(right=0.95)

plt.tight_layout()
plt.savefig(f'figures/articles_per_language.png')
plt.clf()

plt.figure(figsize=(12, 6))
for lang, label, color in languages:
    timestamps, reachables_avg = sampled_data[lang]
    if any(reachables_avg):  
        plt.plot(timestamps, reachables_avg, label=label, color=color)

plt.xlabel("Date")
plt.xticks(rotation=45)
plt.ylabel("Number of Unique, Reachable Providers")
plt.title("Unique Providers")
plt.legend()
ax = plt.gca()  
ax.yaxis.set_major_locator(MaxNLocator(integer=True))
ax.xaxis.set_major_locator(DayLocator())  # Set ticks to start of each day
ax.xaxis.set_major_formatter(DateFormatter('%d.%m.%Y'))  # Display the date in 'dd.mm.yyyy' format

min_date = min([min(sampled_data[lang][0]) for lang, _, _ in languages])
max_date = max([max(sampled_data[lang][0]) for lang, _, _ in languages])

# min_date = min([min(sampled_data[lang]['timestamp']) for lang, _, _ in languages])
# max_date = max([max(sampled_data[lang]['timestamp']) for lang, _, _ in languages])

ax.set_xlim(min_date, max_date)

plt.tight_layout()
plt.savefig(f'figures/unique_reachable_providers_{sample_percentage}_{measurement_name}.png')
