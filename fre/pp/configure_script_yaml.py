#!/usr/bin/env python
"""
    Script creates rose-apps and rose-suite
    files for the workflow from the pp yaml.
"""

import os
import json
import shutil
from jsonschema import validate, ValidationError, SchemaError
import yaml
import click
import metomi.rose.config

######VALIDATE#####
package_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(package_dir, 'schema.json')

def validate_yaml(file):
    """
     Using the schema.json file, the yaml format is validated.
    """
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one
    with open(schema_path) as s:
        schema = json.load(s)

    # Validate yaml
    # If the yaml is not valid, the schema validation will raise errors and exit
    if validate(instance=file,schema=schema) is None:
        print("YAML VALID")

###################
@click.command()

def yamlInfo(yamlfile,experiment,platform,target):
    """
    Using a valid pp.yaml, the rose-app and rose-suite
    configuration files are created in the cylc-src
    directory. The pp.yaml is also copied to the
    cylc-src directory.
    """
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
    # disagreeable; these should be optional
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'],  value='False')
    rose_suite.set(keys=['template variables', 'DO_MDTF'],  value='False')
    rose_suite.set(keys=['template variables', 'PP_DEFAULT_XYINTERP'],  value='0,0')

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

    with open(yml,"r") as f:
        y=yaml.safe_load(f)
        validate_yaml(y)

    for key,value in y.items():
        if key == "rose-suite":
            for suiteconfiginfo,dicts in value.items():
                for configkey,configvalue in dicts.items():
                    if configvalue is not None:
                        k=configkey.upper()
                        if k in ("HISTORY_DIR", "PP_DIR", "ANALYSIS"):
                            # replace generic variables in pp yaml
                            stem=e.split("_",1)[0]
                            exp=e.split("_",1)[1]
                            replacevars=configvalue.replace("$(stem)",stem).replace("$(expname)",exp).replace("$(platform)",p).replace("$(target)",t)
                            rose_suite.set(keys=['template variables', k], value=f'{replacevars}')
                        else:
                            rose_suite.set(keys=['template variables', k], value=f'"{configvalue}"')

        if key == "components":
            for i in value:
                comp = i.get('type')
                sources = i.get('sources')
                interp_method = i.get('interpMethod')

                # set remap items
                rose_remap.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
                # if xyInterp doesnt exist, grid is native
                if i.get("xyInterp") is None:
                    rose_remap.set(keys=[f'{comp}', 'grid'], value='native')
                # if xyInterp exists, component can be regridded
                else:
                    interp_split = i.get('xyInterp').split(',')
                    rose_remap.set(keys=[f'{comp}', 'grid'], value=f'regrid-xy/{interp_split[0]}_{interp_split[1]}.{interp_method}')

                # set regrid items
                if i.get("xyInterp") is not None:
                    rose_regrid.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
                    rose_regrid.set(keys=[f'{comp}', 'inputRealm'], value=f'{i.get("inputRealm")}')
                    rose_regrid.set(keys=[f'{comp}', 'inputGrid'], value=f'{i.get("sourceGrid")}')
                    rose_regrid.set(keys=[f'{comp}', 'interpMethod'], value=f'{interp_method}')
                    interp_split = i.get('xyInterp').split(',')
                    rose_regrid.set(keys=[f'{comp}', 'outputGridLon'], value=f'{interp_split[1]}')
                    rose_regrid.set(keys=[f'{comp}', 'outputGridLat'], value=f'{interp_split[0]}')
                    rose_regrid.set(keys=[f'{comp}', 'outputGridType'], value=f'{interp_split[0]}_{interp_split[1]}.{interp_method}')

    # write output files
    print("Writing output files...")
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")

    outfile = os.path.join(cylc_dir, 'pp.yaml')
    shutil.copyfile(yml, outfile)
    print("  " + outfile)

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
