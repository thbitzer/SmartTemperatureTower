# SmartTemperatureTower

This tool can be used to create GCODE for a 3D-Printer in order to print a heat tower with rising temperature settings. The start-, end- and step-temperature can be chosen freely.

## How it works

1. The main Python script "SmartTemperatureTower.py" runs OpenSCAD with the user-supplied parameters and creates an STL file out of file "SmartTemperatureTower_Stand.stl" and "SmartTemperatureTower_TempFloor.stl". 
2. The rusulting STL file is being converted into a GCODE file using the Prusa Slicer. At each Layer change, a marker is inserted to identify the starting point of a layer.
3. After that, the Python script parses the GCODE and inserts "M104" GCODE commands at the layer start markers of new floors of the temperature tower.

## Requirements

This script has been tested with:

* Python 3.8.3
* OpenSCAD 2019.05
* Prusa Slicer V2.1.0

Although this script has been developed and tested on Windows, it should also run on Linux.

## Installation

Copy the content of this repository into an empty directory and start the execution from here.

## Usage:

* Open a terminal window and change into the directory where the repo was downloaded.
* Execute: python SmartTemperatureTower.py -s 190 -e 240 -t 5

If all goes well, a file named "CalibrationTower-190-240-5.gcode" will be created. It can be uploaded to your 3D-printer.
