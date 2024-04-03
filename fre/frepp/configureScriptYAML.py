#!/usr/bin/env python

import os
import yaml
import click
from jsonschema import validate, ValidationError, SchemaError
import json
import shutil

######VALIDATE#####
package_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(package_dir, 'schema.json')

def validateYaml(file):
  # Load the json schema: .load() (vs .loads()) reads and parses the json in one
  with open(schema_path) as s:
    schema = json.load(s)

  # Validate yaml
  # If the yaml is not valid, the schema validation will raise errors and exit
  if validate(instance=file,schema=schema) == None:
    print("YAML VALID")

###################
@click.command()

def yamlInfo(yamlfile,experiment,platform,target):
  e = experiment
  p = platform
  t = target
  yml = yamlfile

  with open(yml,'r') as f:
    y=yaml.safe_load(f)
    valyml = validateYaml(y)

###################
### Copy pp yaml into cylc-src directory, make rose-suite, then IF remap and regrid paths defined, write those in cylcsrc/app/...

  # Make sure cylc-src exists (it should if this is done after fre checkout) and cd into
  directory = os.path.expanduser("~/cylc-src")
  name = f"{e}__{p}__{t}"
  # Copy pp yaml into ~/cylc-src/name
  shutil.copyfile(yml,directory+"/"+name+"/pp.yaml")  
  # Go into cylc-src directory
  os.chdir(directory+"/"+name)

### PARSE YAML
## Write the rose-suite-exp configuration
  for key,value in y.items():
    if key == "configuration_paths":
      for configname,path in value.items():
        if configname == "rose-suite":
          rs_path = f"{path}/rose-suite-{e}"
        
          # Create rose-suite-exp config
          with open(rs_path,'w') as f:
            f.write('[template variables]\n')
            f.write('## Information for requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')

          print(f"Path: {rs_path} created")

## Populate ROSE-SUITE-EXP config
    if key == "rose-suite":
      if e and p and t:
        with open(rs_path,'a') as f:
          f.write(f'EXPERIMENT="{e}"\n\n')
          f.write(f'PLATFORM="{p}"\n\n')
          f.write(f'TARGET="{t}"\n\n')

      for suiteconfiginfo,dict in value.items():
        for configkey,configvalue in dict.items():
          if configvalue != None:
            with open(rs_path,'a') as f:
              k=configkey.upper()
              if configvalue == True or configvalue == False:
                f.write(f'{k}={configvalue}\n\n')
              else:
                if configkey == "refinediag_scripts":
                  script=configvalue.split("/")[-1]
                  f.write(f'{k}="\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag/{script}"\n\n')
                elif configkey == "preanalysis_script":
                  script=configvalue.split("/")[-1]
                  f.write(f'{k}="\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag/{script}"\n\n')
                else:
                  f.write(f'{k}="{configvalue}"\n\n')

##################################################################################
## Writes regrid-xy and Remap-pp-components rose-app.conf files
    if key == "configuration_paths":
      for configname,path in value.items():
        # Remap-pp-components rose-app.conf
        if configname == "rose-remap" and path != None: # AND VALUE NOT EMPTY:
          remap_roseapp = path
          # Check if filepath exists
          if os.path.exists(remap_roseapp):
            print(f"Path: {remap_roseapp} exists")
          else:
            os.makedirs(remap_roseapp)
            print(f"Path: {remap_roseapp} created")
          with open(remap_roseapp,'w') as f:
            f.write("[command]\n")
            f.write("default=remap-pp-components\n")     
       
        # Regrid-xy rose-app.conf 
        elif configname == "rose-regrid" and path != None: # AND VALUE NOT EMPTY:
          regrid_roseapp = path
          # Check if filepath exists
          if os.path.exists(regrid_roseapp):
            print(f"Path: {regrid_roseapp} exists")
          else:
            os.makedirs(regrid_roseapp)
            print(f"Path: {regrid_roseapp} created")
          with open(regrid_roseapp,'w') as f:
            f.write("[command]\n")
            f.write("default=regrid-xy\n")

## If the rose-remap and rose-regrid paths are defined, populate the associated rose-app.confs
    if key == "components":
      if y.get("configuration_paths")["rose-remap"] != None and y.get("configuration_paths")["rose-regrid"] != None:
        for i in value:
          for compkey,compvalue in i.items():
            # Create/write remap rose app
            with open(remap_roseapp,'a') as f:
              if compkey == "type": 
                f.write(f"\n\n[{compvalue}]\n")
                #if xyInterp doesnt exist, grid is native
                if i.get("xyInterp") == None:
                  f.write(f"grid=native\n")
                #in xyInterp exists, component can be regridded
                elif i.get("xyInterp") != None:
                  f.write("grid=regrid-xy\n") 
                if "static" in compvalue:
                  f.write("freq=P0Y\n")                       
              elif compkey == "sources":
                f.write(f"{compkey}={compvalue} ")
              elif compkey == "timeSeries":
                for i in compvalue:
                  for key,value in i.items():
                    if key == "source":
                      f.write(f"{value} ")

            # Create/write regrid rose app
            with open(regrid_roseapp,'a') as f:
              if i.get("xyInterp") != None: 
                if compkey == "type":
                  f.write(f"\n[{compvalue}]\n")
                  if "atmos" in compvalue:
                    f.write("inputRealm=atmos\n")
                  elif "land" in compvalue:
                    f.write("inputRealm=land\n")
                  elif "river" in compvalue:
                    f.write("inputRealm=land\n")
                  elif "ocean" in compvalue:
                    f.write("inputRealm=ocean\n")
                  elif "aerosol" or "tracer" in compvalue:
                    f.write("inputRealm=atmos\n")
                elif compkey == "sourceGrid": 
                  f.write(f"inputGrid={compvalue}\n")
                elif compkey == "interpMethod":
                  f.write(f"{compkey}={compvalue}\n")
                elif compkey == "sources":
                  f.write(f"{compkey}={compvalue} ")
                  try: 
                    i["timeSeries"]
                    for elem in i['timeSeries']:
                      for key,value in elem.items():
                        if key == "source":
                          f.write(f"{value} ")
                  except:
                    print("No timeseries information")

                  f.write("\n")

                if compkey == "xyInterp" and compvalue == y["define5"]:
                  f.write(f"outputGridType=default\n")
                elif compkey == "xyInterp": 
                  gridLat=compvalue.split(",")[0]
                  gridLon=compvalue.split(",")[1]

                  f.write(f"outputGridLat={gridLat}\n")
                  f.write(f"outputGridLon={gridLon}\n")
                  f.write(f"outputGridType={gridLat}_{gridLon}\n") 
                  
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
