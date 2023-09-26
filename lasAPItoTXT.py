# -*- coding: utf-8 -*
"""
@author: jjcharzynski 
"""

import os
import lasio

def uwis_from_las_files(folder_path, output_file_name):
    """
    Extracts UWI (Unique Well Identifier) values from LAS files in the specified folder path
    and saves them to a text file.

    Parameters:
        folder_path (str): The path to the folder containing LAS files.
        output_file_name (str): The name of the output text file where the UWI values will be saved.

    Returns:
        None
    """
    # Initialize an empty list to store the UWIs
    uwis = []

    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".las"):
            # Use the lasio package to read the UWI from the file
            las_file = lasio.read(os.path.join(folder_path, filename))
            try:
                uwi = las_file.well["UWI"].value
            except KeyError:
                uwi = las_file.well["API"].value
            # Append the UWI to the list
            uwis.append(uwi)

    # Save the list of UWIs to a text file
    with open(output_file_name, "w") as file:
        for uwi in uwis:
            file.write(uwi + "\n")

    print("Text file of UWIs saved to", output_file_name)

# Example usage:
folder_path = "H:\\Fields"
output_file_name = "2023.txt"
uwis_from_las_files(folder_path, output_file_name)