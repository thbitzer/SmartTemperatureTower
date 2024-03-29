# SmartTemperatureTower

This tool can be used to create GCODE for a 3D-Printer in order to print a heat tower with rising temperature settings. The start-, end- and step-temperature can be chosen freely.

## How it works

1. The main Python script "SmartTemperatureTower.py" runs OpenSCAD with the user-supplied parameters and creates a resulting STL file out of "SmartTemperatureTower_Stand.stl" and "SmartTemperatureTower_TempFloor.stl". 
2. That STL file is being converted into a GCODE file using the Prusa Slicer. At each Layer change, a marker is inserted to identify the starting point of that layer.
3. After that, the Python script parses the GCODE and inserts "M104" GCODE commands at the layer start markers of new floors of the temperature tower.

## Requirements

This script has been tested with:

* Python 3.8.3
* OpenSCAD 2019.05
* Prusa Slicer V2.1.0

Although this script has been developed and tested on Windows, it should also run on Linux.

This script uses Python 3 syntax and will not run with Python 2.X!

## Installation

Just clone this repository or download one of the released archives and start the execution from here.

## Configuration

Enter the paths to OpenSCAD, Prusa-Slicer and to Prusa-Slicer's ini files (Open Prusa-Slicer -> Help -> Show Configuration Folder) into the file "SmartTemperatureTower.ini". The file already contains some standard defaults.

In the same ini file (under the [Profile] section), there are 3 Prusa-Slicer profiles to specify (printer, print and filament). All 3 of them are optional, but it is strongly recommended to use them for the temperature tower.

## Usage:

* Open a terminal window and change into the directory where the release package or repo was downloaded.
* Execute: 
  `python SmartTemperatureTower.py -s 190 -e 240 -t 5`

If all goes well, a file named "CalibrationTower-190-240-5.gcode" will be created. It can be uploaded to your 3D-printer.

If you wish to list your PruseSlicer profiles to use them in the init file, please issue one of the following commands:
```
python SmartTemperatureTower.py -l printer
python SmartTemperatureTower.py -l print
python SmartTemperatureTower.py -l filament
```
## How to print this

Take the resulting GCODE file and upload it to your printer. That's it!

**NOTE:** *During the print, the first 2 layers are printed with the default temperature from the filament ini file to ensure proper bed adhesion.*

## Result

This is a SmartTemperatureTower printed on a modified Anet A8 using PETG filament. Temprature range was 220 - 250 degree Celsius and step width was 5 degree Celsius. The bottom "floors" of the tower show less stringing and better bridges, so I have chosen 225 degrees as printing temperature.

![Image of the result](https://github.com/thbitzer/SmartTemperatureTower/raw/master/img/SmartTemperatureTower.jpg "Result")