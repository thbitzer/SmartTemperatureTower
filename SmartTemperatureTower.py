#!/usr/bin/env python

# This script extracts settings from the gcode comments shown below.
# The gcode comments should be added to the filament settings start G-Code in Slic3r
# Each layer should begin with
# ;LAYER:[layer_num]   - where [layer_num] is replaced by the layer number
#
# example Usage: 
#           ./setLayerTemperatur.py -s 215 -e 260 -t 5 -f tempTower_PETG2.gcode
#   or:     ./setLayerTemperatur.py --startTemp=215 --endTemp=260 --tempStep=5 --gcodeFile=tempTower_PETG2.gcode
#

import argparse
import configparser
from os.path import isfile
import re
import subprocess
import sys

# Path to OpenSCAD and Prusa Slicer
cmdOpenScad = "C:\\Program Files\\OpenSCAD\\openscad.com"
cmdPrusaSlicer = "C:\\Program Files\\Prusa3D\\PrusaSlicer\\prusa-slicer-console.exe"

# Open Prusa-Slicer -> Help -> Show Configuration Folder
iniPSD = "C:\\Users\\thbitzer\\AppData\\Roaming\\PrusaSlicer"

# All required data files we need to build a Calibration Tower
requiredFiles = {
    "scadFile": "parameterized_STTMod.scad",
    "stlFloor": "SmartTemperatureTower_TempFloor.stl",
    "stlStand": "SmartTemperatureTower_Stand.stl"
}

# Check if all required data files are present
def checkRequiredFiles():

    for file in requiredFiles.keys():
        if not isfile( requiredFiles[file] ):
            return(0)
    return(1)

# Determine Z-size of a STL
def getSTLZSize(filename):
    sp = subprocess.run([cmdPrusaSlicer, "--info", filename], 
                         capture_output=True, text=True)
    ini = configparser.ConfigParser()
    ini.read_string(sp.stdout)
    return(ini[filename]["size_z"])

###
# MAIN
###

if not checkRequiredFiles():
    print()
    print("ERROR: Cannot find all required files. Please make sure all files")
    print("       listed below are in your current directory.\n")
    for file in requiredFiles.keys():
        print( "   * " + requiredFiles[file] )
    print()
    exit(1)

parser = argparse.ArgumentParser(description="Sets the proper temperatures to the corresponding layers of a gcode file exported from Slic3r. This allows the temperature tower to have different temperatures per block.")
requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument('-s', '--startTemp',   type=int, help="Temperature of the first (lowest) block.", required=True)
requiredNamed.add_argument('-e', '--endTemp',     type=int, help="Temperature of the last (highest) block.", required=True)
requiredNamed.add_argument('-t', '--tempStep',    type=int, help="Temperature change between blocks.",       required=True)
requiredNamed.add_argument('-f', '--gcodePrefix',           help="Prefix for gcode file",                    required=False)
args = parser.parse_args()

# Get name for gcode file
if args.gcodePrefix == None:
    gcodePrefix = "CalibrationTower"
else:
    gcodePrefix = args.gcodePrefix
gcodeFile = gcodePrefix + "-" + str(args.startTemp) + "-" + str(args.endTemp) + "-" + str(args.tempStep) + ".gcode"

print("startTemp: {}".format(args.startTemp))
print("endTemp:   {}".format(args.endTemp))
print("tempStep:  {}".format(args.tempStep))
print("gcodeFile: {}".format(gcodeFile))


###
# STEP 1: Create STL file of Calibration Tower using OpenSCAD
###
print("* Create STL file ", end="", flush=True)
rc = subprocess.run( [ cmdOpenScad, "-o", "CT_Temp.stl",
                       "-D", "tfirst=" + str(args.startTemp), "-D", "tlast=" + str(args.endTemp), 
                       "-D", "tstep=" + str(args.tempStep), requiredFiles["scadFile"] ],
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True )

if rc.returncode != 0:
    print("- ERROR: RC != 0")
    print("Error output was:")
    print(rc.stdout)
    print()
    exit(1)
print("- OK")

###
# STEP 2: Create GCODE file using Prusa Slicer
###
print("* Create GCODE file ", end="", flush=True)
rc = subprocess.run( [ cmdPrusaSlicer, "--printer-technology", "FFF",
                                       "--center", "120,120", 
                                       "--before-layer-gcode", ";CT_LAYER:[layer_num]",
                                       "--load", iniPSD+"\\printer\\Anet A8 Standard (advanced priming).ini",
                                       "--load", iniPSD+"\\print\\Anet A8 Standard.ini",
                                       "--load", iniPSD+"\\filament\\PETG - Light Green.ini",
                                       "--export-gcode", "--loglevel", "1",
                                       "--output", "CT_Temp.gcode", "CT_Temp.stl" ],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True )
if rc.returncode != 0:
    print("- ERROR: RC != 0")
    print("Error output was:")
    print(rc.stdout)
    print()
    exit(1)
print("- OK")

floorZSize = getSTLZSize(requiredFiles["stlFloor"])
floorLayer=round(float(floorZSize)/0.2)
nextChange=0 # Zero is the first layer
nextTemp=args.startTemp

###
# STEP 3: Insert M104 (set temp) on floor changes
###
print("* Create GCODE file ", end="", flush=True)
gcodeInput = open("CT_Temp.gcode", 'r')
gcodeOutput = open(gcodeFile, 'w')
for LINE in gcodeInput:
    gcodeOutput.write(LINE)
    if re.match('^;CT_LAYER:[0-9]+$', LINE):
        lineNum = int(re.sub('^;CT_LAYER:([0-9]+)','\\1',LINE))
        if lineNum == nextChange:
            gcodeOutput.write("M104 S" + str(nextTemp) + '\n')
            nextChange+=floorLayer
            nextTemp+=args.tempStep    

gcodeInput.close()
gcodeOutput.close()
print("- OK")

exit(0)
