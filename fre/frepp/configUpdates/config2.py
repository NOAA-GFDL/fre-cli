#!/usr/bin/env python

import os
import yaml
import click
from jsonschema import validate, ValidationError, SchemaError
import json

######VALIDATE#####
package_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(package_dir, 'schema-pp.json')

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
@click.option("-y",
              type=str,
              help="YAML file to be used for parsing",
              required=True)

#maybe change name to parseYaml
def yamlInfo(y):
#file="pp.yaml"
  with open(y,'r') as f:
    y=yaml.safe_load(f)
    yml = validateYaml(y)

#PARSE YAML
## Write the rose-suite-exp configuration
  for key,value in y.items():
    #print(key)

    ## Add: check paths?
    if key == "configuration_paths":
      #print(value)
      for filename,path in value.items():
        if filename == "rose-suite":
          rs = path
          # Create rose-suite-exp config
          with open(rs,'w') as f:
            f.write('[template variables]\n')
            f.write('## Information for requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')
    
        ## STILL CREATE ROSE APPS FOR NOW (regrid and remap)
        elif filename == "rose-remap":
          remap_roseapp = path
          with open(remap_roseapp,'w') as f:
            f.write("[command]\n")
            f.write("default=remap-pp-components\n")            
        elif filename == "rose-regrid":
          regrid_roseapp = path
          with open(regrid_roseapp,'w') as f:
            f.write("[command]\n")
            f.write("default=regrid-xy\n")

## Populate ROSE-SUITE-EXP config
    if key == "rose-suite":
      #print(value)
      for suiteconfiginfo,dict in value.items():
        #print(value)
        for configkey,configvalue in dict.items():
          #print(value)
          if configvalue != None:
            with open(rs,'a') as f:
              k=configkey.upper()
              if configvalue == True or configvalue == False:
                f.write(f'{k}={configvalue}\n\n')
              else:
                if "pp_start" in configkey:
                  f.write(f'{k}="{configvalue}OOTZ"\n\n')
                elif "pp_stop" in configkey:
                  f.write(f'{k}="{configvalue}OOTZ"\n\n')
                else:
                  f.write(f'{k}="{configvalue}"\n\n')

##if value of type is in remap AND regrid grid value in remap rose app=regrid-xy
    if key == "regrid-remap-info":
      for components,compinfo in value.items():
        for i in compinfo:
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

              elif compkey == "sources":
                f.write(f"{compkey}={compvalue} ")
              elif compkey == "timeSeries":
                #print(compvalue)
                for i in compvalue:
                  #print(i)  
                  for key,value in i.items():
                    if key == "source":
                      f.write(f"{value} ")

            # Create/write regrid rose app
            with open(regrid_roseapp,'a') as f:
              # if xyInterp is defined, that is a regridded component
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
                    f.write("inputRealm=aerosol\n")
                elif compkey == "sourceGrid": 
                  f.write(f"inputGrid={compvalue}\n")
                elif compkey == "interpMethod":
                  f.write(f"{compkey}={compvalue}\n")
                elif compkey == "sources":
                  f.write(f"{compkey}={compvalue} ")
                  if i["timeSeries"]:
                    for elem in i['timeSeries']:
                      for key,value in elem.items():
                        if key == "source":
                          f.write(f"{value} ")
                  f.write("\n")
                    
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
