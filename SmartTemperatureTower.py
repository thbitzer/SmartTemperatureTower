#!/usr/bin/env python

# This script extracts settings from the gcode comments shown below.
# The gcode comments should be added to the filament settings start G-Code in Prusa-Slicer
# Each layer should begin with
# ;CT_LAYER:[layer_num]   - where [layer_num] is replaced by the layer number
#
# example Usage: 
#           ./SmartTemperatureTower.py -s 215 -e 260 -t 5
#

import argparse
import configparser
from os.path import isfile,isdir
import os
import re
import subprocess
import sys

### Defaults section

# Path to OpenSCAD and Prusa Slicer
cmdOpenScad = "C:\\Program Files\\OpenSCAD\\openscad.com"
cmdPrusaSlicer = "C:\\Program Files\\Prusa3D\\PrusaSlicer\\prusa-slicer-console.exe"

# Open Prusa-Slicer -> Help -> Show Configuration Folder
iniPSD = os.environ["APPDATA"]+"\\PrusaSlicer"

# All required data files we need to build a Calibration Tower
requiredFiles = {
    "scadFile": "parameterized_STTMod.scad",
    "stlFloor": "SmartTemperatureTower_TempFloor.stl",
    "stlStand": "SmartTemperatureTower_Stand.stl"
}

### Functions

# Get option from ini file. If not present or empty, use default
def getOpt(iniSect, name, default):
    if name in iniSect and iniSect[name] != "":
        return(iniSect[name])
    else:
        return(default)
        
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

# Print error messaga about missing tools or profiles
def toolNotFound(toolname,toolpath):
    print("ERROR: The "+toolname+" is not available on the system.")
    print("")
    print("       Expected at:")
    print("       "+toolpath)


###
# MAIN
###

### Check for config file and override defaults if desired

# Read configuration
cfgFile="SmartTemperatureTower.ini"
if isfile(cfgFile):
    cfg = configparser.ConfigParser()
    cfg.read(cfgFile)

    cmdOpenScad = getOpt(cfg["Path"], "openscad", cmdOpenScad)
    cmdPrusaSlicer = getOpt(cfg["Path"], "prusa_slicer", cmdPrusaSlicer)
    iniPSD = getOpt(cfg["Path"], "prusa_slicer_ini", iniPSD)

    printProfile = getOpt(cfg["Profile"], "print", "")
    printerProfile = getOpt(cfg["Profile"], "printer", "")
    filamentProfile = getOpt(cfg["Profile"], "filament", "")

# Check configured paths
if not isfile(cmdOpenScad):
    toolNotFound("OpenSCAD tool",cmdPrusaSlicer)
    exit(1)
if not isfile(cmdPrusaSlicer):
    toolNotFound("Prusa-Slicer tool",cmdPrusaSlicer)
    exit(1)
if not isdir(iniPSD):
    toolNotFound("Prusa-Slicer profile dir", iniPSD)
    exit(1)

# Check configured profiles
profiles = []
if printProfile != "":
    printProfile = iniPSD+"\\print\\"+printProfile
    if not isfile(printProfile):
        toolNotFound("Prusa-Slicer print profile", printProfile)
    else:
        profiles.append(printProfile)
if printerProfile != "":
    printerProfile = iniPSD+"\\printer\\"+printerProfile
    if not isfile(printerProfile):
        toolNotFound("Prusa-Slicer printer profile", printerProfile)
    else:
        profiles.append(printerProfile)
if filamentProfile != "":
    filamentProfile = iniPSD+"\\filament\\"+filamentProfile
    if not isfile(filamentProfile):
        toolNotFound("Prusa-Slicer filament profile", filamentProfile)
    else:
        profiles.append(filamentProfile)

loadProfiles = ""
loadProfilesList = []
for profile in profiles:
    loadProfilesList.append("--load")
    loadProfilesList.append(profile)
    if loadProfiles == "":
        loadProfiles = "--load "+profile
    else:
        loadProfiles += " --load "+profile

if not checkRequiredFiles():
    print()
    print("ERROR: Cannot find all required files. Please make sure all files")
    print("       listed below are in your current directory.\n")
    for file in requiredFiles.keys():
        print( "   * " + requiredFiles[file] )
    print()
    exit(1)

parser = argparse.ArgumentParser(description="Create a gcode file to print a Heat Calibration Tower.")
requiredNamed = parser.add_argument_group('required arguments')
requiredNamed.add_argument('-s', '--startTemp', type=int, help="Temperature of the first (lowest) block.")
requiredNamed.add_argument('-e', '--endTemp', type=int, help="Temperature of the last (highest) block.")
requiredNamed.add_argument('-t', '--tempStep', type=int, help="Temperature change between blocks.")
parser.add_argument('-p', '--gcodePrefix', help="Prefix for gcode file")
parser.add_argument('-l', '--profiles', nargs='?', help="List printer profiles (PROFILES=print, printer, filament)")
args = parser.parse_args()


# List printer profiles
if args.profiles != None:
    validIniDirs=["printer","print","filament"]
    if not args.profiles in validIniDirs:
        print()
        print("ERROR: Unknown ini path: "+args.profiles)
        print()
        print("       Valid paths are:")
        for path in validIniDirs:
            print("       * "+path)
        print()
        sys.exit(1)
    path=iniPSD+"\\"+args.profiles
    iniarr = os.listdir(path)
    print()
    print("Printer profiles available in directory:")
    print(path)
    print()
    for ini in iniarr:
        print("* "+ini)
    print()
    sys.exit(0)

# Check that all required arguments are given
if args.startTemp == None or args.endTemp == None or args.tempStep == None:
    parser.print_help()
    sys.exit(1)

# Get name for gcode file
if args.gcodePrefix == None:
    gcodePrefix = "CalibrationTower"
else:
    gcodePrefix = args.gcodePrefix

    # We don't want a full filename with extension for the -p (prefix) parameter
    if re.search('\\.', args.gcodePrefix):
        ext=re.sub('^.*(\\..*)$', '\\1', args.gcodePrefix)
        print("ERROR: The -p / --gcodePrefix parameter contains an extension ("+ext+").")
        exit(1)
        
gcodeFile = gcodePrefix + "-" + str(args.startTemp) + "-" + str(args.endTemp) + "-" + str(args.tempStep) + ".gcode"

print()
print("Start Temperature: {}".format(args.startTemp))
print("End Temperature:   {}".format(args.endTemp))
print("Temperature Step:  {}".format(args.tempStep))
print("Printer Profile:   {}".format(printerProfile))
print("Print Profile:     {}".format(printProfile))
print("Filament Profile:  {}".format(filamentProfile))
print("gcodeFile:         {}".format(gcodeFile))
print()

###
# STEP 1: Create STL file of Calibration Tower using OpenSCAD
###
print("* Create STL file ", end="", flush=True)
if isfile("CT_Temp.stl"):
    os.remove("CT_Temp.stl")
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
if isfile("CT_Temp.gcode"):
    os.remove("CT_Temp.gcode")
rc = subprocess.run( [ cmdPrusaSlicer, "--loglevel", "2", "--printer-technology", "FFF",
                                       "--center", "120,120", 
                                       "--before-layer-gcode", ";CT_LAYER:[layer_num]",
                                       *loadProfilesList,
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


###
# STEP 3: Insert M104 (set temp) on floor changes
###
floorZSize = getSTLZSize(requiredFiles["stlFloor"])
floorLayer=round(float(floorZSize)/0.2)
firstChange=2 # Start at layer 2, so we use default temp for bottom 2 layers
nextChange=firstChange
nextTemp=args.startTemp

print("* Add M104 commands ", end="", flush=True)
gcodeInput = open("CT_Temp.gcode", 'r')
gcodeOutput = open(gcodeFile, 'w')
for LINE in gcodeInput:
    gcodeOutput.write(LINE)
    if re.match('^;CT_LAYER:[0-9]+$', LINE):
        lineNum = int(re.sub('^;CT_LAYER:([0-9]+)','\\1',LINE))
        if lineNum == nextChange:
            gcodeOutput.write("M104 S" + str(nextTemp) + '\n')
            if nextChange == firstChange:
                nextChange=floorLayer
            else:
                nextChange+=floorLayer
            nextTemp+=args.tempStep    

gcodeInput.close()
gcodeOutput.close()
print("- OK")

exit(0)
