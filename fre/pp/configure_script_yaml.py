#!/usr/bin/env python

import os
import yaml
import click
from jsonschema import validate, ValidationError, SchemaError
import json
import shutil
import metomi.rose.config

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

  # initialize rose suite config
  rose_suite = metomi.rose.config.ConfigNode()
  rose_suite.set(keys=['template variables', 'SITE'],              value='"ppan"')
  rose_suite.set(keys=['template variables', 'CLEAN_WORK'],        value='True')
  rose_suite.set(keys=['template variables', 'PTMP_DIR'],          value='"/xtmp/$USER/ptmp"')
  rose_suite.set(keys=['template variables', 'DO_STATICS'],        value='True')
  rose_suite.set(keys=['template variables', 'DO_TIMEAVGS'],       value='True')
  rose_suite.set(keys=['template variables', 'DO_ATMOS_PLEVEL_MASKING'], value='True')

  # initialize rose regrid config
  rose_regrid = metomi.rose.config.ConfigNode()
  rose_regrid.set(keys=['command', 'default'], value='regrid-xy')

  # initialize rose remap config
  rose_remap = metomi.rose.config.ConfigNode()
  rose_remap.set(keys=['command', 'default'], value='remap-pp-components')

  # set some rose suite vars
  rose_suite.set(keys=['template variables', 'EXPERIMENT'], value=f'"{e}"')
  rose_suite.set(keys=['template variables', 'PLATFORM'], value=f'"{p}"')
  rose_suite.set(keys=['template variables', 'TARGET'], value=f'"{t}"')

  with open(yml,'r') as f:
    y=yaml.safe_load(f)
    valyml = validateYaml(y)

###################
### Copy pp yaml into cylc-src directory, make rose-suite, then IF remap and regrid paths defined, write those in cylcsrc/app/...

  # Make sure cylc-src exists (it should if this is done after fre checkout) and cd into
  # Copy pp yaml into ~/cylc-src/name
  cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
  shutil.copyfile(yml, os.path.join(cylc_dir, 'pp.yaml')  )
  # verify the directory exists
  os.chdir(cylc_dir)

### PARSE YAML
## Write the rose-suite-exp configuration
  for key,value in y.items():
    if key == "configuration_paths":
      for configname,path in value.items():
        if configname == "rose-suite":
          rs_path = f"{path}/rose-suite.conf"

## Populate ROSE-SUITE-EXP config
    if key == "rose-suite":
      for suiteconfiginfo,dict in value.items():
        for configkey,configvalue in dict.items():
          if configvalue != None:
            k=configkey.upper()
            rose_suite.set(keys=['template variables', k], value=f'{configvalue}')

## If the rose-remap and rose-regrid paths are defined, populate the associated rose-app.confs
    if key == "components":
      if y.get("configuration_paths")["rose-remap"] != None and y.get("configuration_paths")["rose-regrid"] != None:
        for i in value:
          for compkey,compvalue in i.items():
            # Create/write remap rose app
            if compkey == "type": 
              f.write(f"\n\n[{compvalue}]\n")
              #if xyInterp doesnt exist, grid is native
              if i.get("xyInterp") == None:
                f.write(f"grid=native\n")
              #in xyInterp exists, component can be regridded
              elif i.get("xyInterp") != None and i.get("xyInterp") == y["defaultxyInterp"]:
                f.write("grid=regrid-xy/default\n") 
              elif i.get("xyInterp") != None and i.get("xyInterp") != y["defaultxyInterp"]:
                gridLat=i.get("xyInterp").split(",")[0]
                gridLon=i.get("xyInterp").split(",")[1]
                f.write(f"grid=regrid-xy/{gridLat}_{gridLon}\n")
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

                if compkey == "xyInterp" and compvalue == y["defaultxyInterp"]:
                  f.write(f"outputGridType=default\n")
                elif compkey == "xyInterp": 
                  gridLat=compvalue.split(",")[0]
                  gridLon=compvalue.split(",")[1]

                  f.write(f"outputGridLat={gridLat}\n")
                  f.write(f"outputGridLon={gridLon}\n")
                  f.write(f"outputGridType={gridLat}_{gridLon}\n") 

  # write rose configs
  print("Writing output files...")
  os.chdir(cylc_dir)
  dumper = metomi.rose.config.ConfigDumper()
  outfile = "rose-suite.conf"
  dumper(rose_suite, outfile)
  print("  " + outfile)
  outfile = "app/regrid-xy/rose-app.conf"
  dumper(rose_regrid, outfile)
  print("  " + outfile)
  outfile = "app/remap-pp-components/rose-app.conf"
  dumper(rose_remap, outfile)
  print("  " + outfile)
                  
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
