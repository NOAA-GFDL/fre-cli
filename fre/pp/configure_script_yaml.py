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

    if key == "rose-suite":
      for suiteconfiginfo,dict in value.items():
        for configkey,configvalue in dict.items():
          if configvalue != None:
            k=configkey.upper()
            rose_suite.set(keys=['template variables', k], value=f'{configvalue}')

    if key == "components":
      for i in value:
        comp = i.get('type')
        sources = i.get('sources')
        interp_method = i.get('interpMethod')

        # set remap items
        rose_remap.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
        # if xyInterp doesnt exist, grid is native
        if i.get("xyInterp") == None:
          rose_remap.set(keys=[f'{comp}', 'grid'], value='native')
        # if xyInterp exists, component can be regridded
        else:
          gridLat=i.get("xyInterp").split(",")[0]
          gridLon=i.get("xyInterp").split(",")[1]
          rose_remap.set(keys=[f'{comp}', 'grid'], value=f'regrid-xy/{gridLat}_{gridLon}')

        # set regrid items
        if i.get("xyInterp") != None:
          rose_regrid.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
          rose_regrid.set(keys=[f'{comp}', 'inputRealm'], value=f'{i.get("inputRealm")}')
          rose_regrid.set(keys=[f'{comp}', 'inputGrid'], value=f'{i.get("inputGrid")}')
          rose_regrid.set(keys=[f'{comp}', 'interpMethod'], value=f'{interp_method}')
          interp_split = i.get('xyInterp').split(',')
          rose_regrid.set(keys=[f'{comp}', 'outputGridLon'], value=f'{interp_split[1]}')
          rose_regrid.set(keys=[f'{comp}', 'outputGridLat'], value=f'{interp_split[0]}')

  # write rose configs
  print("Writing output files...")
  os.chdir(cylc_dir)
  dumper = metomi.rose.config.ConfigDumper()
  outfile = os.path.join(cylc_dir, "rose-suite.conf")
  dumper(rose_suite, outfile)
  print("  " + outfile)
  outfile = os.path.join(cylc_dir, "app", "regrid-xy", "rose-app.conf")
  dumper(rose_regrid, outfile)
  print("  " + outfile)
  outfile = os.path.join(cylc_dir, "app", "remap-pp-components", "rose-app.conf")
  dumper(rose_remap, outfile)
  print("  " + outfile)
                  
# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
