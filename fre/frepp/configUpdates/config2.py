#!/usr/bin/env python

import os
from pathlib import Path
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
      for key,value in value.items():
        if key == "rose-suite":
          rs = value
          # Create rose-suite-exp config
          with open(rs,'w') as f:
            f.write('[template variables]\n')
            f.write('## Information for requested postprocessing, info to pass to refineDiag/preanalysis scripts, info for epmt, and info to pass to analysis scripts \n')
    
        ## STILL CREATE ROSE APPS FOR NOW (regrid and remap)
        elif key == "rose-remap":
          remap_roseapp = value
          with open(remap_roseapp,'w') as f:
            f.write("[command]\n")
            f.write("default=remap-pp-components\n")            
        elif key == "rose-regrid":
          regrid_roseapp = value
          with open(regrid_roseapp,'w') as f:
            f.write("[command]\n")
            f.write("default=regrid-xy\n")

## Populate ROSE-SUITE-EXP config
    if key == "rose-suite":
      #print(value)
      for key,value in value.items():
        #print(value)
        for key,value in value.items():
          #print(value)
          if value != None:
            with open(rs,'a') as f:
              k=key.upper()
              if value == True or value == False:
                f.write(f'{k}={value}\n\n')
              else:
                if "pp_start" in key:
                  f.write(f'{k}="{value}OOTZ"\n\n')
                elif "pp_stop" in key:
                  f.write(f'{k}="{value}OOTZ"\n\n')
                else:
                  f.write(f'{k}="{value}"\n\n')     

##if value of type is in remap AND regrid grid value in remap rose app=regrid-xy
###for inputRealm: if atmos in key, atmos, same with land and ocean
    if key == "regrid-remap-info":
      #print(key)
      for key,value in value.items():
        for i in value:
          #print(i)
          for key,value in i.items():
            #print(value)
            with open(remap_roseapp,'a') as f:
              if key == "type":
                f.write(f"\n[{value}]\n")
              if key != "type":
                f.write(f"{key}={value}\n")

