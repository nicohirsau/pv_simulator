import csv
import os

def file_append(filepath, content):
    """
    This method will take a list of values and appends it
    as a new row to a csv file.
    If the file does not exist, it will be created.

    Params:
        filepath: The path to the file that should be written to.
        content: A list of values that should be appended.
    """
    with open(filepath, "a") as f:
        writer = csv.writer(f)
        writer.writerow(content)
