import csv
import os
import glob
from typing import List, Tuple, Dict

# Languages to process
languages: List[str] = ['en', 'ru', 'uk', 'tr', 'my', 'zh', 'fa', 'ar']

def load_csv_files(providers_csv: str, detailed_cid_csv: str) -> None:
    """
    Load data from CSV files, process it and write it to a new file.

    Args:
        providers_csv: The path to the providers csv file.
        detailed_cid_csv: The path to the detailed cid csv file.

    """
    try:
        with open(providers_csv, 'r', newline='') as file_a_obj:
            unreachable_providers: List[str] = []
            csv_reader_a = csv.reader(file_a_obj)
            _ = next(csv_reader_a)  # Skip the header row
            for row in csv_reader_a:
                reachable = row[2]
                if reachable.lower() == "false":
                    unreachable_providers.append(row[0])

    except FileNotFoundError:
        print(f"File '{providers_csv}' not found.")

    try:
        updated_rows: List[List[str]] = []
        with open(detailed_cid_csv, 'r', newline='') as file_b_obj:
            csv_reader_b = csv.reader(file_b_obj)
            headers = next(csv_reader_b)  # Skip the header row
            updated_rows.append(headers)

            for row in csv_reader_b:
                provider_list = row[4].split(',')
                reachable_providers = [p for p in provider_list if p and p not in unreachable_providers]
                row[4] = ','.join(reachable_providers)
                row[3] = len(reachable_providers)
                updated_rows.append(row)

        # Write the updated rows to a new CSV file
        with open(detailed_cid_csv[:-4] + '_cleaned.csv', 'w', newline='') as updated_file_obj:
            csv_writer = csv.writer(updated_file_obj)
            csv_writer.writerows(updated_rows)

    except FileNotFoundError:
        print(f"File '{detailed_cid_csv}' not found.")

def find_matching_files(language: str, subfolder: str) -> List[Tuple[str, str]]:
    """
    Find matching file pairs in the provided folder.

    Args:
        language: The language code string.
        subfolder: The subfolder name.

    Returns:
        A list of tuples where each tuple contains paths of a matching file pair.
    """
    folder = os.path.join('./data', str(language), str(subfolder))
    cid_path = os.path.join(folder, 'CID', '*.csv')
    provider_path = os.path.join(folder, 'Providers', '*.csv')

    cid_files: Dict[str, str] = {os.path.basename(file): file for file in glob.glob(cid_path)}
    provider_files: Dict[str, str] = {os.path.basename(file): file for file in glob.glob(provider_path)}

    matching_files = [(provider_files[file_name], cid_files[file_name]) for file_name in provider_files if file_name in cid_files]

    return matching_files

def find_subfolders(language: str) -> List[str]:
    """
    Find subfolders in the provided language folder.

    Args:
        language: The language code string.

    Returns:
        A list of subfolder names.
    """
    subfolders: List[str] = []
    language_folder = os.path.join('./data', str(language))
    if os.path.isdir(language_folder):
        subfolders = os.listdir(language_folder)
    return subfolders

if __name__ == "__main__":
    for l in languages:
        subfolders = find_subfolders(l)
        for subfolder in subfolders:
            matching_file_pairs = find_matching_files(l, subfolder)
            if not matching_file_pairs:
                print(f"No matching file pairs found in {l} for subfolder '{subfolder}'")
            else:
                for providers_csv, detailed_cid_csv in matching_file_pairs:
                    load_csv_files(providers_csv, detailed_cid_csv)
