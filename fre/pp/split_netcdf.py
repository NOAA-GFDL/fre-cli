 #!/bin/python

# Split NetCDF files by variable
#
# Can be tiled or not. Component is optional, defaults to all.
#
# Input format:  date.component(.tileX).nc
# Output format: date.component.var(.tileX).nc

import os
from os import path
import glob
import subprocess
#import cdo
import sys
from pathlib import Path

#Set variables
inputDir = os.environ['inputDir']
outputDir = os.environ['outputDir']
date = os.environ['date']
component = os.environ['component']
use_subdirs = os.environ['use_subdirs'] 

print("Arguments:")
print("    input dir: "+inputDir)
print("    output dir: "+outputDir)
print("    date: "+date)
print("    component: "+component)
print("    use subdirs: "+use_subdirs)
print("Utilities:")
#type(cdo)

#Verify input directory exists and is a directory
if inputDir == "":
    print("Error: Input directory "+ inputDir + " does not exists or isnt a directory")
    sys.exit(1)

#Verify output directory exists and is a directory
if outputDir == "":
    print("Error: Output directory" + outputDir + " does not exist or isn't a directory")
    sys.exit(1)

#Find files to split
#extend globbing used to find both tiled and non-tiled files
curr_dir = os.getcwd()
workdir = os.path.abspath(inputDir)
os.chdir(workdir)

#If in sub-dir mode, process the sub-directories instead of the main one
if use_subdirs:
    for subdir in os.listdir():
        recent_dirs=[]
        recent_dirs.append(subdir)   #pushd
#        files-glob.glob(
        files=glob.glob('*'+'.'+component+'?'+'(.tile?)'+'.nc')
        #files=$(echo *.$component?(.tile?).nc)
        
        # Exit if no input files found 
        if len(files) == 0:
             print("No input files found, skipping the subdir "+subdir)
             os.chdir(recent_dirs[-2])   #popd
             continue

        # Create output subdir if needed
        os.mkdir(os.path.abspath(outputDir)/subdir)

        # Split the files by variable
        # Note: cdo may miss some weird land variables related to metadata/cell_measures
        for file in files:
             newfile = subprocess.call(["sed 's/nc$//' {file}"],shell=True)
#             subprocess.call("cdo --history splitname $file $outputDir/$subdir/$(echo $file | sed 's/nc$//')", shell=True)
             cdo=Cdo()
             cdo.splitname(input=file, 
                           output='outputDir/subdir/newfile')
             #cdo --history splitname file outputDir/subdir/newfile
        
        os.chdir(recent_dirs[-2])   #popd     
else:
    files=glob.glob('*'+'.'+component+'?'+'(.tile?)'+'.nc')
    # Exit if not input files are found
    if len(files) == 0:
        print("ERROR: No input files found")
        sys.exit(1)
 
    # Split the files by variable
    for file in files:
        #newfile=file | sed 's/nc$//'
        newfile = subprocess.call(["sed 's/nc$//' {file}"],shell=True)
        cdo=Cdo()
        cdo.splitname(input=file, 
                      output='outputDir/newfile')
        #cdo --history splitname file outputDir/newfile
  
print("Natural end of the NetCDF splitting")
sys.exit(0) #check this

