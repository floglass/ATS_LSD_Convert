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
LSD: 2
RA: 3 West (RW)

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
