#!/usr/bin/env python
"""
    Script creates rose-apps and rose-suite
    files for the workflow from the pp yaml.
"""

## TO-DO:
# - condition where there are multiple pp yamls
# - validation here or in combined-yamls tools

import os
import json
import shutil
import click

from jsonschema import validate
import yaml
import metomi.rose.config

# Relative import
#f = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(f)
import fre.yamltools.combine_yamls as cy

####################
def yaml_load(yamlfile):
    """
    Load the given yaml and validate.
    """
    # Load the main yaml and validate
    with open(yamlfile,'r') as f:
        y=yaml.safe_load(f)

    return y

######VALIDATE#####
def validate_yaml(yamlfile):
    """
     Using the schema.json file, the yaml format is validated.
    """
    # Load the yaml
    yml = yaml_load(yamlfile)

    package_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(package_dir, 'schema.json')
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one
    with open(schema_path,'r') as s:
        schema = json.load(s)

    # Validate yaml
    # If the yaml is not valid, the schema validation will raise errors and exit
    if validate(instance=yml,schema=schema) is None:
        print("COMBINED YAML VALID \n")

####################
def rose_init(experiment,platform,target):
    """
    Initialize the rose suite and app configurations.
    """
    # initialize rose suite config
    rose_suite = metomi.rose.config.ConfigNode()
    # disagreeable; these should be optional
    rose_suite.set(keys=['template variables', 'DO_ANALYSIS_ONLY'],  value='False')
    rose_suite.set(keys=['template variables', 'DO_MDTF'],  value='False')
    rose_suite.set(keys=['template variables', 'PP_DEFAULT_XYINTERP'],  value='0,0')

    # set some rose suite vars
    rose_suite.set(keys=['template variables', 'EXPERIMENT'], value=f'"{experiment}"')
    rose_suite.set(keys=['template variables', 'PLATFORM'], value=f'"{platform}"')
    rose_suite.set(keys=['template variables', 'TARGET'], value=f'"{target}"')

    # initialize rose regrid config
    rose_regrid = metomi.rose.config.ConfigNode()
    rose_regrid.set(keys=['command', 'default'], value='regrid-xy')

    # initialize rose remap config
    rose_remap = metomi.rose.config.ConfigNode()
    rose_remap.set(keys=['command', 'default'], value='remap-pp-components')

    return(rose_suite,rose_regrid,rose_remap)

####################
def quote_rose_values(value):
    """
    rose-suite.conf template variables must be quoted unless they are
    boolean, in which case do not quote them.
    """
    if isinstance(value, bool):
        return f"{value}"
    else:
        return "'" + value + "'"

####################
def set_rose_suite(yamlfile,rose_suite):
    """
    Set items in the rose suite configuration.
    """
    pp=yamlfile.get("postprocess")
    dirs=yamlfile.get("directories")

    # set rose-suite items
    if pp is not None:
        for i in pp.values():
            if not isinstance(i,list):
                for key,value in i.items():
                    # rose-suite.conf is somewhat finicky with quoting
                    # cylc validate will reveal any complaints
                    rose_suite.set( keys = ['template variables', key.upper()],
                                    value = quote_rose_values(value) )
    if dirs is not None:
        for key,value in dirs.items():
            rose_suite.set(keys=['template variables', key.upper()], value=quote_rose_values(value))

####################
def set_rose_apps(yamlfile,rose_regrid,rose_remap):
    """
    Set items in the regrid and remap rose app configurations.
    """
    components = yamlfile.get("postprocess").get("components")
    for i in components:
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
            rose_remap.set(keys=[f'{comp}', 'grid'],
                           value=f'regrid-xy/{interp_split[0]}_{interp_split[1]}.{interp_method}')

        # set regrid items
        if i.get("xyInterp") is not None:
            rose_regrid.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
            rose_regrid.set(keys=[f'{comp}', 'inputRealm'], value=f'{i.get("inputRealm")}')
            rose_regrid.set(keys=[f'{comp}', 'inputGrid'], value=f'{i.get("sourceGrid")}')
            rose_regrid.set(keys=[f'{comp}', 'interpMethod'], value=f'{interp_method}')
            interp_split = i.get('xyInterp').split(',')
            rose_regrid.set(keys=[f'{comp}', 'outputGridLon'], value=f'{interp_split[1]}')
            rose_regrid.set(keys=[f'{comp}', 'outputGridLat'], value=f'{interp_split[0]}')
            rose_regrid.set(keys=[f'{comp}', 'outputGridType'],
                            value=f'{interp_split[0]}_{interp_split[1]}.{interp_method}')

####################
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

    # Initialize the rose configurations
    rose_suite,rose_regrid,rose_remap = rose_init(e,p,t)

    # Combine model, experiment, and analysis yamls
    comb = cy.init_pp_yaml(yml,e,p,t)
    full_combined = cy.get_combined_ppyaml(comb)

    # Validate yaml
    validate_yaml(full_combined)

    # Load the combined yaml
    comb_pp_yaml = yaml_load(full_combined)

    ## PARSE COMBINED YAML TO CREATE CONFIGS
    # Set rose-suite items
    set_rose_suite(comb_pp_yaml,rose_suite)

    # Set regrid and remap rose app items
    set_rose_apps(comb_pp_yaml,rose_regrid,rose_remap)

    # write output files
    print("Writing output files...")
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")
    shutil.copyfile(full_combined, outfile)
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

@click.command()
def _yamlInfo(yamlfile,experiment,platform,target):
    '''
    Wrapper script for calling yamlInfo - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return yamlInfo(yamlfile,experiment,platform,target)

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
