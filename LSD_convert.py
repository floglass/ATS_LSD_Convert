"""
Script allowing to convert a bunch of LSD positions (following the Alberta Township System, v4.1 2005) into latitude
and longitude.

The Alberta Township System (ATS, based on the Domain Land Survey) identifies plots of lands on a grid using the
following format:

LSD - Section - Township - Range   Meridian

example:

07-27-072-03 W4

meaning (reading right to left)
West of meridian 4,   Valid meridians are 4, 5, or 6
range 3 (3*6 miles wide column),  Valid ranges are 1 to 30 (inclusive)
township 72 (72*6 miles wide rows starting at southern Canadian border (126 max)), Valid township are 1 to 126
section 27 (divide township into 1x1 mile squares (36 total) and count them boustrophedonically from southeast corner),
legal subdivision 7 (divide section into 4x4 quadrant (16 total) and count them boustrophedonically from southeast).

To convert this ATS location into lat/lon, a conversion table is used.
The conversion table was retrieved from https://www.altalis.com/ and should be the latest in use.

The data is a modified version of the ATS_polygon dataset from altalis. Latitude and Longitude has been added
to each LSD by using the position of the centroid of the polygon. The data is in GIS format, which contains latitudes
and longitudes, but has been reformatted to .csv.

The format of the original file is as follow:
-----------------------------------------
Data        Field Length        Columns
-----------------------------------------
PID         13                  1-14
File_Name   8                   15-23
TRM         8                   24-32
M           3                   33-36
RGE         3                   37-40
TWP         3                   41-44
SEC         3                   45-48
QS          2                   49-51
LS          3                   52-55
Descriptor  34                  56-90
RA          var
-----------------------------------------
Geometry
-----------------------------------------
PID should have all the data we need to identify the position in ATS:
Meridian (1) Range (2) Township (3) Section (2) LSD (2) RA (1)
Number in bracket is the number of place holders
Example: 42804302023
Meridian: 4
Range: 28
Township: 43
Section: 2
LSD:2
RA: West (RW)

The reformatted dataset is as follow:
-----------------------------------------
Data        Field Length        Columns
-----------------------------------------
PID         13                  1-12
Latitude    17                  13-30
Longitude   19                  31-50
-----------------------------------------

This script will:
Take a batch ASCII file containing ATS positions (one per line)
In a loop:
    Check that ATS is in Alberta
    Convert the ATS format into a PID
    Compare it to the database, and find the match
    Extract the Latitude and Longitude from the database
    Append to an output file with ATS and Lat Lon
Export the result in a csv file

TODO: use of python "simplekml" or "pyKML" to directly create the kml (kmz?) file.
"""

import pandas as pd
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from pathlib import Path


def check_ats(ats=None):
    """Check that ATS is in Alberta
    Format for ATS is 7-27-72-3 W4
    Meridian [4,5,6]
    Range [1 to 30]
    Township [1 to 126]
    Section [1 to 36]
    LSD [1 to 16]
    """
    # create ranges of acceptable values
    ats_meridian = [i+1 for i in range(3, 6)]
    ats_range = [i+1 for i in range(30)]
    ats_township = [i+1 for i in range(126)]
    ats_section = [i+1 for i in range(36)]
    ats_lsd = [i+1 for i in range(16)]

    # format the input ATS into a list
    ats_mod = ats.replace(' W', '-')
    ats_list = ats_mod.split('-')
    ats_list = [int(ats_list[i]) for i in range(len(ats_list))]

    # check each element of the list are within range of acceptable values
    meridian_ok = ats_list[4] in ats_meridian
    range_ok = ats_list[3] in ats_range
    township_ok = ats_list[2] in ats_township
    section_ok = ats_list[1] in ats_section
    lsd_ok = ats_list[0] in ats_lsd

    # Raise error if ATS is not in Alberta
    if [lsd_ok, section_ok, township_ok, range_ok, meridian_ok] == [True, True, True, True, True]:
        pass
    else:
        raise ValueError('ATS position not inside range of acceptable values')
    return ats_list


def ats_to_numeral(ats=None):
    """
    Input the ATS, and format it into the PID: one chain of numerals in the format:
    Meridian(1)Range(2)Township(3)Section(2)LSD(2)  (in brackets are place number of holders)
    :param ats: LSD-Section-Township-Range WMeridian
    :return: string
    """
    temp = re.sub(pattern=' W', repl='-', string=ats, flags=re.IGNORECASE)
    temp = temp.split('-')
    temp[0] = temp[0].zfill(2)
    temp[1] = temp[1].zfill(2)
    temp[2] = temp[2].zfill(3)
    temp[3] = temp[3].zfill(2)
    temp[4] = temp[4].zfill(1)
    numeral_out = ''
    for i in reversed(temp):
        numeral_out += i
    return numeral_out


def compare_to_database(numeral=None, database=None, ats=None, path=None):
    """
    Compare "numeral" (PID) to the database's PID, and return [latitude, longitude]
    :param numeral: output of ats_to_numeral, in format Meridian(1)Range(2)Township(3)Section(2)LSD(2)
    :param database: the ATS polygon v4.1, edited with latitudes and longitudes.
    :param ats: the ATS location, in LSD-section-township-range meridian
    :param path: path to log folder (containing "duplicates")
    :return: [latitude, longitude] corresponding to the ATS position
    """
    row = database.loc[database['PID'].str.contains(numeral)]
    # print(row)
    if len(row) > 1:  # if there are several entries with the same PID (due to road allowance)
        select_pid = '{}0'.format(numeral)  # select PID with Road Allowance == 0
        # save a copy of the duplicates (for verification)
        print("Multiple elements for PID {} in database, adding to '_duplicates.csv'. \n{}".format(numeral, row))
        with open('{}\\Logs\\_duplicates.csv'.format(path), 'a') as dpl:
            dpl.write("{}\n".format(ats))
            dpl.write(row.to_string(header=False, index=False))
            dpl.write('\n')  # add a new line after the dataframe

        row = row.loc[row['PID'] == select_pid]  # select the proper PID

    latitude = float(row['Latitude'])
    longitude = float(row['Longitude'])
    latlon = [latitude, longitude]
    return latlon


def load_database(database_path=None):
    """
    Read the Alberta Township System v4.1 database of parcels, and store it in a pandas.DataFrame
    :param database_path: Path to the database
    :return: a pandas.DataFrame of all the parcels of land in the ATS
    """
    if database_path is None:
        database_path = 'D:\\Lite-Step\\ATS-LSD\\ATS_Polygons_SHP_Geographic\\ATS_V4-1_LSD_wLatLon.csv'

    df = pd.read_csv(database_path, header=0)
    df = df.astype({"PID": str})  # convert column "PID" into a string
    # df['PID'] = df['PID'].str[:10]  # remove last digit of PID string, corresponding to RA
    return df


def load_targets(target_list=None):
    """ target_list contains 'LSD' (and optionally 'Trees') for all targets
    :return: a pandas.DataFrame of all targets"""
    targets = pd.read_csv(target_list)  # creates a pandas.DataFrame
    return targets


def check_against_batch(target_path=None):
    """
    Take a list of target LSDs (optional with Trees number) and convert it to Latitude Longitude.
    If Trees numbers are present, will also add a column "Trees" and "Name" (format of name: "LSD | Trees") to the
    results for easy integration with Google Maps markers (with my.maps)
    :param target_path: path to target list in .csv form
    :return: 'results', 'dataframe_load', 'targets'
    :type: DataFrames
    """
    dataframe_load = load_database()
    targets = load_targets(target_path)
    current_path = target_path.rsplit('/', maxsplit=1)[0]
    print(current_path)
    Path("{}\\Logs".format(current_path)).mkdir(exist_ok=True)  # create a directory "Logs" if it doesn't already exist
    f = open('{}\\Logs\\_duplicates.csv'.format(current_path), 'w')  # create empty "_duplicates.csv"
    f.close()

    # check if the target list also have tree numbers (needs a different output if it does)
    if 'Trees' in targets.columns:
        trees_exist = True
    else:
        trees_exist = False
    results = {}

    # convert ATS into Lat Lon
    for i in range(len(targets)):
        ats = targets.loc[i, 'LSD']
        print("--------------------\nProcessing {}..".format(targets.loc[i]))
        numeral = ats_to_numeral(ats)
        print("Comparing {} to database..".format(numeral))
        latlon_i = compare_to_database(numeral, dataframe_load, ats, current_path)
        if trees_exist:
            trees = int(targets.loc[i, "Trees"])
            name_i = "{} | {}".format(ats, trees)
            results[i] = [ats, numeral, latlon_i[0], latlon_i[1], trees, name_i]  # Ats, PID, Lat, Lon, Trees, Name
        else:
            results[i] = [ats, numeral, latlon_i[0], latlon_i[1]]  # Ats, PID, Lat, Lon

    # Dict to DataFrame
    if trees_exist:
        results = pd.DataFrame.from_dict(results, orient='index', columns=['LSD', 'PID', 'Latitude', 'Longitude',
                                                                           'Trees', 'Name'])
    else:
        results = pd.DataFrame.from_dict(results, orient='index', columns=['LSD', 'PID', 'Latitude', 'Longitude'])

    # save file and return results, dataframe (the whole Alberta Township System), and targets for debugging
    print("..Done")
    results_file = asksaveasfilename(title="Please save your results as", filetypes=(("CSV Files", "*.csv"),))
    results.to_csv(results_file, index=False)
    return results, dataframe_load, targets


def main():
    print("Please select the list of LSDs you want to convert:\n"
          "The first line should be a header with 'LSD' and optionally 'Trees'\n"
          "The accepted format of the data is: LSD - Section - Township - Range   Meridian\n"
          "Example: 07-27-72-3 W4\n"
          "Optional: A column 'Trees' can be added with tree numbers for each site.")
    Tk().withdraw()  # keep the root window from appearing (no need of full GUI)
    # show an "open" dialog box and return the path of the selected file
    target_file = askopenfilename(title="Please select the file containing the LSDs you want to convert",
                                  filetypes=(("CSV Files", "*.csv"),))
    check_against_batch(target_file)


if __name__ == "__main__":
    main()
