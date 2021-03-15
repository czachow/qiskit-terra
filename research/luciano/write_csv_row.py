import csv
from os.path import isfile

"""
{'seed': seed,
 'ideal': {
    'time',
    counts_dict'},
 'noise': {
    'time',
    counts_dict'}
}
"""


def write_csv_row(filename, row_dict):
    header = not isfile(filename)

    with open(filename, 'a', newline='') as csvfile:
        fieldnames = row_dict.keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if header:
            writer.writeheader()
        writer.writerow(row_dict)
