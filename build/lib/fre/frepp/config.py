#!/usr/bin/env python

# Author: Dana Singh
# Description: Script parses user-edit yaml, creates/implements the changes in rose-suite-exp.conf, rose-app.conf, bin/install-exp, and checks that filepaths exist

# import os
# from pathlib import Path
# import yaml
import click
# from jsonschema import validate, ValidationError, SchemaError
# import json

####################
# Function to parse and validate user defined edits.yaml 
def parseyaml(file):
    # Load yaml
    with open(file,'r') as f:
        y=yaml.safe_load(f)

    ## TO-DO: validate user-yaml
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one
    with open("schema.json") as s:
        schema = json.load(s)
    
    # Validate yaml
    # If the yaml is not valid, the schema validattion will raise errors and exit
    if validate(instance=y,schema=schema) == None:
        print("YAML VALID")
 
    # Start parsing the yaml
    d=[]
    for k1 in y:
        for k2 in y[k1]:
            for dict in y[k1][k2]:
                d.append(dict)
    return d   #list,list of dictionaries

####################
@click.command()
@click.argument('yamlfile', nargs=1)
def yamlInfo(yamlfile):
    yml = parseyaml(yamlfile)
    # Parse information in dictionary 
    for items in yml:
        for key,value in items.items():
            # Define paths in yaml
            if key == 'path' and value != None:
                p=Path(value)

## ROSE-SUITE-EXP-CONFIG EDITS ##
            # Create rose-suite-exp.conf and populate it with user-defined edits in edits.yaml
            if key == "rose-suite-exp-configuration":
                with open(p,'w') as f:
                    f.write('[template variables]\n')
                    f.write('## Information for requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')
                print(f"{key} CREATED in {p}")
 
                for key,value in value.items():
                    # If there is a defined value in the yaml, create and write to a rose-suite-EXP.conf
                    if value != None:
                        with open(p,'a') as f:
                            # Add in comment for experiment specific information
                            if key == "HISTORY_DIR":
                                f.write("## Information about experiment\n")

                            # If value is of type boolean, do not add quotes in configuration. If the value is a string, write value in configuration with quotes.
                            if value == True or value == False:
                                f.write(f'{key}={value}\n\n')
                            else:
                                f.write(f'{key}="{value}"\n\n')
  
## ROSE-APP-CONFIG EDITS ##
            # Open and write to rose-app.conf for regrid-xy and remap-pp-components 
            # Populate configurations with info defined in edits.yaml; path should exist
            if p.exists() == True and key == "rose-app-configuration":
                ## Check if filepath exists
                print(f"Path to {p} EXISTS")

                #regrid-xy and remap-pp-components 
                for v in value:
                    for key,value in v.items():
                         #write file and close; ensures file always starts with command and default fields
                         with open(p,'w') as f:
                             f.write("[command]\n")
                             if "regrid-xy" in str(p):
                                 f.write("default=regrid-xy\n")
                             elif "remap-pp-components" in str(p):
                                 f.write("default=remap-pp-components\n")

                         for k in value:
                             for key,value in k.items():
                                 if value != None:
                                     # Append defined regrid and remap information from yaml
                                     with open(p,"a") as f:
                                         # Component is written on own line with brackets, followed by information for that component
                                         if key == "type":
                                             f.write(f"\n[{value}]\n")
                                         if key != "type":
                                             f.write(f"{key}={value}\n")
           
            ## If path does not exist, output error message
            elif p.exists() == False and key == "rose-app-configuration":
                print(f"ERR: Path {p} DOES NOT EXIST")
    
## INSTALL-EXP SCRIPT EDIT ##
            # If alternate path for cylc-run directory defined in edits.yaml, add symlink creation option onto cylc install command
            # The file should exist, hence the file is read and lines are replaced with defined values in the yaml.
            if p.exists() == True and key == "install-option": 
                ## Check if filepath exists
                print(f"Path to {p} EXISTS")

                for key,value in value.items():
                    with open(p,"r") as f:
                        rf=f.readlines()
                        if value != None:
                            for line in rf:
                                #for optional cylc install addition edit
                                if "cylc install -O" in line:
                                    line_num=rf.index(line)
                                    rf[line_num]='cylc install -O $1 --workflow-name $1 '+value+'\n'
                                    with open(p,'w') as f:
                                        for line in rf:
                                            f.write(line)

            ## If path does not exist, output error message
            elif p.exists() == False and key == "install-option":
                print(f"ERR: Path {p} DOES NOT EXIST")

## TMPDIR PATH EDIT ##
            if key == "tmpdirpath":
                tmppath = Path(value)

                ## If path does exists, output message; if path does not exist, create tmp directory and output message
                if tmppath.exists():
                    print(f"Path to TMPDIR: {value} EXISTS")
                else:
                    os.mkdir(value)
                    print(f"TMPDIR: {value} was CREATED")

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()