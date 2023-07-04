import csv

input_file = 'nginx-HTTP_referrer_requests_only.csv'
output_file = 'nginx-HTTP_referrer_requests_only_sorted.csv'

# Load the data from the CSV file
data = []
with open(input_file, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
        data.append(row)

# Sort the data based on the 11th and 12th column - the user agent and the http referrer (URL)
sorted_data = sorted(data, key=lambda x: (x[10], x[11]))

# Write the sorted data to a new CSV file
with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for row in sorted_data:
        writer.writerow(row)