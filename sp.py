import subprocess
import configparser

subprocess = subprocess.run(["\"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer-console.exe\"",
                            "--info", "SmartTemperatureTower_Stand_fixed.stl"], capture_output=True)
subprocess_return = subprocess.stdout.read()
print(subprocess_return)

ini = configparser.ConfigParser()
ini.read_string(subprocess_return)
for a in ini.sections:
    print(a)