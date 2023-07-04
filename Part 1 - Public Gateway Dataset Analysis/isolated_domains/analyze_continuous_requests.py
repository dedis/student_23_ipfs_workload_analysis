import pandas as pd
import matplotlib.pyplot as plt
import sys

input_file = str(sys.argv[1])
plot_name = input_file[:-17]

# Load the CSV file into a pandas dataframe
df = pd.read_csv(input_file)

# Create the histograms
plt.hist(df['num_requests'], bins=50)
plt.title('Grouped Requests - Requests per Group')
plt.ylabel('Group Count')
plt.xlabel('Requests per Group')
plt.savefig(f"{plot_name}_requests.png")
plt.clf()

plt.hist(df['duration'] / 60, bins=30)
# plt.xscale('log')
plt.title('Grouped Requests - Duration')
plt.ylabel('Group Count')
plt.xlabel('Duration [Minutes]')
plt.savefig(f"{plot_name}_durations.png")
plt.clf()

plt.hist(df['Bytes_returned_average'] / (1024 * 1024), bins='auto')
plt.title('Grouped Requests - Average Response Size')
plt.ylabel('Group Count')
plt.xlabel('Average Response Size [MB]')
plt.savefig(f"{plot_name}_avg_response_sizes.png")
plt.clf()

plt.hist(df['Total_bytes_returned'] / (1024 * 1024), bins='auto')
plt.title('Grouped Requests - Total Response Size')
plt.ylabel('Group Count')
plt.xlabel('Total Response Size [MB]')
plt.savefig(f"{plot_name}_total_response_sizes.png")
plt.clf()

plt.hist(df['Success_ratio'], bins=20)
plt.title('Grouped Requests - Success Ratio per Group')
plt.ylabel('Group Count')
plt.xlabel('Success Ratio')
plt.savefig(f"{plot_name}_success_ratio.png")
plt.clf()

plt.hist(df['Cache_hit_ratio'], bins=20)
plt.title('Grouped Requests - Cache Hit Ratio per Group')
plt.ylabel('Group Count')
plt.xlabel('Cache Ratio')
plt.savefig(f"{plot_name}_cache_hit_ratio.png")
plt.clf()