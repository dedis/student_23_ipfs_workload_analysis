import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple

# Load the CSV data
data: pd.DataFrame = pd.read_csv('extracted_URLs.csv')

def aggregate_data(data: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
    """
    Group data by 'Website Type', sum the 'Occurrences' and count the number of rows for each type.
    Also calculate the total number of occurrences across all types.
    """
    # Group the data by 'Website Type' and sum the 'Occurrences'
    grouped_data = data.groupby('Website Type')['Occurrences'].sum().reset_index()

    # Group the data by 'Website Type' and count the number of rows
    row_count_data = data.groupby('Website Type').size().reset_index(name='Row_Count')

    # Merge the two dataframes on 'Website Type'
    grouped_data = pd.merge(grouped_data, row_count_data, on='Website Type')

    # Calculate the total number of occurrences
    total_occurrences = grouped_data['Occurrences'].sum()

    return grouped_data, total_occurrences

def handle_less_contributing_types(grouped_data: pd.DataFrame, total_occurrences: float) -> pd.DataFrame:
    """
    Create a new 'Other' category for website types with less than 1% contribution.
    Remove the less contributing types and add the 'Other' category.
    """
    # Create a new 'Other' category for website types with less than 1% contribution
    grouped_data['Percentage'] = (grouped_data['Occurrences'] / total_occurrences) * 100
    other_data = grouped_data[grouped_data['Percentage'] < 1].sum(numeric_only=True)
    other_data['Website Type'] = 'Other'

    # Remove the less contributing types and add the 'Other' category
    grouped_data = grouped_data[grouped_data['Percentage'] >= 1].append(other_data, ignore_index=True)
    
    return grouped_data

def plot_pie_chart(grouped_data: pd.DataFrame) -> None:
    """
    Plot a pie chart for the given data.
    """
    # Generate enough colors from the colormap for each website type
    colors = plt.cm.tab20c(np.linspace(0.2, 1, len(grouped_data)))

    # Create new labels with the number of rows in brackets as integers
    new_labels = [f"{label} ({int(count)} Websites)" for label, count in zip(grouped_data['Website Type'], grouped_data['Row_Count'])]

    # Plot the pie chart
    fig, ax = plt.subplots(figsize=(10, 6))
    wedges, texts, autotexts = ax.pie(grouped_data['Occurrences'], labels=new_labels, autopct='%1.1f%%', colors=colors)
    ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular

    # Set font size for labels and percentages
    for text in texts + autotexts:
        text.set_fontsize(12)

    # Set the title and display the chart
    plt.title('HTTP Referrals: Content Type', fontsize=18)
    plt.savefig('URL_pie_chart_with_types.png')
    plt.show()

grouped_data, total_occurrences = aggregate_data(data)
grouped_data = handle_less_contributing_types(grouped_data, total_occurrences)
plot_pie_chart(grouped_data)
