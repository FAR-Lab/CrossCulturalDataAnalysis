"""
Introduction:
The idea is that even if there are modules like https://github.com/grst/nbimporter,
as the author of that repo wrote, importing notebook into other notebooks is not a good practice
This python file serves the purpose of containing all the utility scrips that don't deal with graphics
ex: file reading, file picking, data processing, etc.

Normally I would first develop the functions in the notebook and move them to this python file
if they are frequently used. The original function in notebook would not be deleted.

Also, sorry for my functions' naming format not being formal python convention.
If somebody is bothered by it please feel free to refactor
"""

import matplotlib.pyplot as plt
import pandas
import re
from pathlib import Path
import numpy as np
import random
import os

# Iterate through all folders in the same directory and put scenario CSVs into dictionary
# Return: CSV dictionary -- key: CP name, value: list of paths
def GetCSVDictionary():
    # get current working directory then set folder path
    cwd = os.getcwd()
    folder_path = Path(cwd) / 'Data'

    # Create a dictionary to store the CP paths
    csv_categorized = {}

    # Iterate over all csv files
    for file in folder_path.rglob('*.csv'):  # "r"glob for recursive
        # Check filename pattern
        filename = file.name
        # (\d+) tries to match and catch any number of digits
        # use https://regex101.com to check and modify regex if file name pattern changes in the future
        match = re.match(r'CSVScenario-CP(\d+)_Session-.+_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.csv', filename)
        if match:
            # Use the capture to get CP number
            crosspath_number = match.group(1)

            if crosspath_number not in csv_categorized:
                csv_categorized[crosspath_number] = [file]
            else:
                csv_categorized[crosspath_number].append(file)

    # Print categorized csv files
    for crosspath_number, files in csv_categorized.items():
        print(f'CP{crosspath_number} - {len(files)} ')
    return csv_categorized

# the previous GetCSVDictionary is already quite complex, don't want to couple too hard
# also, python doesn't have function overloading (whyyyy) so I'm just creating a new function
# make sure location variable is always 3 character string
def GetCSVDictionaryByLocation(location):
    cwd = os.getcwd()
    folder_path = Path(cwd) / 'Data'
    csv_categorized = {}
    for file in folder_path.rglob('*.csv'):
        # Check filename pattern
        filename = file.name
        match = re.match(r'CSVScenario-CP(\d+)_Session-(.{3})\d+_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.csv', filename)
        if match:
            if match.group(2) == location:
                crosspath_number = match.group(1)
                if crosspath_number not in csv_categorized:
                    csv_categorized[crosspath_number] = [file]
                else:
                    csv_categorized[crosspath_number].append(file)
    for crosspath_number, files in csv_categorized.items():
        print(f'CP{crosspath_number} - {len(files)} ')
    return csv_categorized


def PickRandomFromCP(cp_num, cp_dictionary):
    if cp_num in cp_dictionary:
        return random.choice(cp_dictionary[cp_num])
    else:
        raise ValueError(f"No CP {cp_num}")


def GetScenarioCSVList(cp_num, validity, location = "all"):
    cwd = os.getcwd()
    validity_csv = Path(cwd) / f'Data/DataValidity/CP{cp_num}/path_validity_CP{cp_num}_cleaned_followGPS.csv'

    def GetAllValidCSV(isValid):
        validity_df = pandas.read_csv(validity_csv, sep=";")

        # Filter out only valid files
        valid_files_df = validity_df[validity_df['Validity'] == isValid]

        # Print the valid files
        i = 0
        temp_path = []
        if location.lower() == "all":
            for index, row in valid_files_df.iterrows():
                temp_path.append(row['Path'])
                i += 1
            print(f"got {i} csv from CP{cp_num} with validity: {validity}")
            return temp_path
        else:
            for index, row in valid_files_df.iterrows():
                match = re.match(r'.*CSVScenario-CP(\d+)_Session-(.{3})\d+_\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.csv',
                                 row['Path'])
                if match:
                    if match.group(2) == location:
                        temp_path.append(row['Path'])
                        i += 1
            print(f"got {i} csv from CP{cp_num} in {location} with validity: {validity} ")
            return temp_path
    return GetAllValidCSV(validity)

# return: dataframe
def GetTruncatedScenario(path, wantedDistanceWithin):
    df = pandas.read_csv(path, sep=';')

    # LIM for limit --- X>-LIM, X<LIM, Y>-LIN, Y<LIM
    dfA = df[((df['HeadPosXA'] > -wantedDistanceWithin) & (df['HeadPosXA'] < wantedDistanceWithin)) & (
                (df['HeadPosZA'] > -wantedDistanceWithin) & (df['HeadPosZA'] < wantedDistanceWithin))]
    dfB = df[((df['HeadPosXB'] > -wantedDistanceWithin) & (df['HeadPosXB'] < wantedDistanceWithin)) & (
                (df['HeadPosZB'] > -wantedDistanceWithin) & (df['HeadPosZB'] < wantedDistanceWithin))]
    return dfA, dfB



#-------------------plotting-------------------------
def DrawIntersectionFromPath(path, wantedDistanceWithin):
    zoomFactor = 40
    dfA, dfB = GetTruncatedScenario(path, wantedDistanceWithin)

    plt.plot(dfA['HeadPosXA'], dfA['HeadPosZA'], label="Car A", color='red')
    plt.plot(dfB['HeadPosXB'], dfB['HeadPosZB'], label="Car B", color='blue')

    plt.plot([-wantedDistanceWithin, -wantedDistanceWithin], [-wantedDistanceWithin, wantedDistanceWithin],
             color='black')
    plt.plot([-wantedDistanceWithin, wantedDistanceWithin], [wantedDistanceWithin, wantedDistanceWithin], color='black')
    plt.plot([wantedDistanceWithin, wantedDistanceWithin], [wantedDistanceWithin, -wantedDistanceWithin], color='black')
    plt.plot([wantedDistanceWithin, -wantedDistanceWithin], [-wantedDistanceWithin, -wantedDistanceWithin],
             color='black')

    # Define the number of ticks you want to see on the x and y axes
    ticks_x = np.linspace(-zoomFactor, zoomFactor, num=40, dtype=int)
    ticks_y = np.linspace(-zoomFactor, zoomFactor, num=40, dtype=int)

    plt.xticks(ticks_x, fontsize=5)  
    plt.yticks(ticks_y, fontsize=5)

    plt.grid(True)  # Ensure that the grid is on

    plt.xlim([-zoomFactor, zoomFactor])
    plt.ylim([-zoomFactor, zoomFactor])
    plt.legend()
    return plt


# -------------------misc-------------------------
def get_variable_name(var, globals=globals()):
    return [var_name for var_name, var_val in globals.items() if var_val is var]
