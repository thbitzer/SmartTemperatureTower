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

import argparse, sys
from os.path import isfile
import subprocess

cmdOpenScad = "C:\\Program Files\\OpenSCAD\\openscad.com"
cmdPrusaSlicer = "C:\\Program Files\\Prusa3D\\PrusaSlicer\\prusa-slicer-console.exe"

# Open Prusa-Slicer -> Help -> Show Configuration Folder
iniPSD = "C:\\Users\\thbitzer\\AppData\\Roaming\\PrusaSlicer"

# All required data files we need to build a Calibration Tower
requiredFiles = {
    "scadFile": "parameterized_STTMod.scad",
    "stlFloor": "SmartTemperatureTower_TempFloor.stl",
    "stlStand": "SmartTemperatureTower_Stand_fixed.stl"
}

# Check if all required data files are present
def checkRequiredFiles():

    for file in requiredFiles.keys():
        if not isfile( requiredFiles[file] ):
            return(0)
    return(1)

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
requiredNamed.add_argument('-s', '--startTemp', type=int, help="Temperature of the first (lowest) block.", required=True)
requiredNamed.add_argument('-e', '--endTemp',   type=int, help="Temperature of the last (highest) block.", required=True)
requiredNamed.add_argument('-t', '--tempStep',  type=int, help="Temperature change between blocks.",       required=True)
requiredNamed.add_argument('-f', '--gcodeFile',           help="The final .gcode file",                    required=True)
args = parser.parse_args()

print("startTemp: {}".format(args.startTemp))
print("endTemp:   {}".format(args.endTemp))
print("tempStep:  {}".format(args.tempStep))
print("gcodeFile: {}".format(args.gcodeFile))


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
                                       "--before-layer-gcode", ";LAYER:[layer_num]",
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
exit(0)

# parse gcode files
try:
    gcodeInput = open("CT_Temp.gcode" 'r')
    gcodeOutput = open(args.gcodeFile, 'w')
    currentLayerNr=10
    currentTemp=args.startTemp
    layerList=[]
    step=args.tempStep
    # depending if temperature should rise or decrease in layers we need to make sure we get the direction of step right:
    if args.startTemp < args.endTemp:
        step = abs(step)
    else:
        step = abs(step) * -1
    print("step: {}".format(step))
    
    # make the list of layers where temperature needs to be changed        
    for i in range(args.startTemp,args.endTemp+step,step):
        #print("currentTemp: {}".format(currentTemp));
        layerList.append(";LAYER:" + str(currentLayerNr) + '\n')
        #print("-> layerLine: \"{}\"".format(layerList[-1]))
        currentLayerNr+=35
        currentTemp+=step
        
    currentLayer=10
    currentTemp=args.startTemp
    currentLayerStr=layerList.pop(0)

    for LINE in gcodeInput:
        gcodeOutput.write(LINE)
        if currentLayerStr != "" and LINE.find(currentLayerStr)!=-1:
            #print("LINE:            \"{}\"".format(LINE))
            #print("currentLayerStr: \"{}\"".format(currentLayerStr))
            # beginning from layer 10 insert after each 35th layer the right temperature gcode ( M019 ).
            gcodeOutput.write("M104 S" + str(currentTemp) + '\n')
            print("-> M104 S" + str(currentTemp) )
            currentTemp+=step
            if layerList: 
                currentLayerStr=layerList.pop(0)
            else:
                currentLayerStr = ""
except (IOError, OSError) as e:
    print ("I/O error({0}) in \"{1}\": {2}".format(e.errno, e.filename, e.strerror))
except: #handle other exceptions such as attribute errors
   print ("Unexpected error:", sys.exc_info()[0])
else:
    gcodeInput.close()
    gcodeOutput.close()
