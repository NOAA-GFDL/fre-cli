#!/usr/bin/env python

import os
import yaml
import click
from jsonschema import validate, ValidationError, SchemaError
import json

file="pp.yaml"
with open(file,'r') as f:
    y=yaml.safe_load(f)

#first dictionary 
#print(y)

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
                f.write(f"\n[{compvalue}]\n")

                #if xyInterp doesnt exist, grid is native
                if i.get("xyInterp") == None:
                  f.write(f"grid=native\n")

                #in xyInterp exists, component can be regridded
                elif i.get("xyInterp") != None:
                  f.write("grid=regrid-xy\n")                       

#              if key != "type":
#                f.write(f"{key}={value}\n")

              elif compkey == "sources":
                f.write(f"{compkey}={compvalue}\n")

            # Create/write regrid rose app
            with open(regrid_roseapp,'a') as f:
              if i.get("xyInterp") != None:
                if compkey == "type":
                  f.write(f"\n[{compvalue}]\n")
                  if "atmos" in compvalue:
                    f.write(f"inputRealm=atmos\n")
                  elif "land" in compvalue:
                    f.write(f"inputRealm=land\n")
                  elif "ocean" in compvalue:
                    f.write(f"inputRealm=ocean\n")
                elif compkey == "sources":
                  f.write(f"{compkey}={compvalue}\n")
                elif compkey == "sourceGrid":
                  f.write(f"inputGrid={compvalue}\n")
                elif compkey == "interpMethod":
                  f.write(f"{compkey}={compvalue}\n")

##TO-DO
#validation
#fix sources
