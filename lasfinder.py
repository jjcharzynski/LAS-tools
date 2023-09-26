# -*- coding: utf-8 -*-
"""
@author: jjcharzynski
"""
import os
import shutil
import lasio 
import time
import re

def copy_files_with_matching_uwi(src_folder, dest_folder, uwi_file):
    """
    Copy LAS files from a source folder to a destination folder based on a list of matching UWI (Unique Well Identifier).

    Args:
        src_folder (str): The path to the source folder where LAS files are located.
        dest_folder (str): The path to the destination folder where matching LAS files will be copied.
        uwi_file (str): The path to a text file containing a list of UWIs to match against LAS files.

    Returns:
        None

    This function walks through the files in the `src_folder` and its subfolders, reads the LAS files,
    extracts the UWI from each file, and checks if it matches any of the UWIs in the `uwi_file`. If a match is found,
    the LAS file is copied to the `dest_folder`.

    Note:
        - LAS files are expected to have a '.las' extension.
        - The UWI is extracted from LAS files by checking both the 'UWI' and 'API' fields in the LAS header.
        - Files with errors while reading or finding UWI/API are logged in an error file.

    Example:
        src_folder = "C:\\Logs"
        dest_folder = "C:\\Fields"
        uwi_file = r"C:\LASsearch.txt"
        copy_files_with_matching_uwi(src_folder, dest_folder, uwi_file)
    """

    start_time=time.time()
    # Create the destination folder if it does not already exist
    if not os.path.exists(dest_folder): 
        os.makedirs(dest_folder)
        
    # Read the list of UWIS from the text file
    with open(uwi_file, 'r') as f:
        uwi_list = [line.strip()[:10] for line in f.readlines()] 
    
    # Walk through all the files in the source folder and its subfolders
    error_files=[] 
    for root, dirs, files in os.walk (src_folder):
        for file in files:
            # Only process .las files 
            if file.endswith(". Las"):
                file_path= os.path.join(root, file) 
                try:
                    # Load the .las file using lasio
                    las = lasio.read(file_path)
                except Exception as e:
                        print(f"Error reading {file_path}: {e}") 
                        error_files.append(file_path)
                else:
                    # Check if the UWI of the file is in the list of desired UWIS
                    try:
                        file_uwi = las.well["UWI"].value
                        file_uwi = re.sub('[-]','',file_uwi) 
                        file_uwi = file_uwi[:10]
                        if file_uwi in uwi_list:
                            # Copy the file to the destination folder
                            dest_path = os.path.join(dest_folder, file)
                            shutil.copy2 (file_path, dest_path)
                            print("Copied (file_path) to (dest_path}")
                    except KeyError:
                        # print(f"Error finding UWI trying API instead for {file}.")
                        try: 
                            file_api = las.well["API"].value 
                            file_api = re.sub('[-]','',file_api)
                            file_api = file_api[:10] 
                            if file_api in uwi_list:
                                # Copy the file to the destination folder
                                dest_path= os.path.join(dest_folder, file)
                                shutil.copy2(file_path, dest_path) 
                                print("Copied (file_path) to (dest_path}")
                        except KeyError:
                            print("Error finding UNI and API for {file}.")
                            error_files.append(file_path)
            else:
                print("(file) is not an LAS file.")

    step_time=time.time()
    error_txt=str(f"Lasfindererrors{step_time}.txt") 
    with open(error_txt, "w") as output:
        output.write(str(error_files))
        end_time=time.time()
        duration=end_time-start_time
        print(f"Completed in {duration} seconds.")