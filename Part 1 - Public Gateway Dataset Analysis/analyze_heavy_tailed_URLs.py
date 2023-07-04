import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
data = pd.read_csv("extracted_URLs.csv")

# Sort the data by occurrences in descending order
data_sorted = data.sort_values(by="Occurrences", ascending=False)

# Mass-disparity count plot (Zipf plot)
plt.figure()
plt.loglog(data_sorted["Occurrences"].values, linestyle="-", marker="o")
plt.xlabel("Website Rank")
plt.ylabel("Requests generated")
plt.title("Mass-disparity Count (Zipf) Plot")
plt.grid()
plt.savefig('URL_mass_disparity_count.png')
# plt.show()

# Pareto rule plot (CDF plot)
cdf = data_sorted["Occurrences"].cumsum() / data_sorted["Occurrences"].sum()
x_values = np.arange(1, len(cdf) + 1) / len(cdf)

plt.figure()
plt.plot(x_values, cdf, linestyle="-", marker="o")
plt.xlabel("Percentage of Websites")
plt.ylabel("Cumulative Percentage of Requests")
plt.title("Pareto Rule (CDF) Plot")
plt.grid()
plt.savefig('URL_pareto_rule.png')
# plt.show()