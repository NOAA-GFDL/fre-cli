#!/usr/bin/env python
"""
    Script creates rose-apps and rose-suite
    files for the workflow from the pp yaml.
"""

## TO-DO:
# - figure out way to safe_load (yaml_loader=yaml.SafeLoader?)
# - condition where there are multiple pp yamls

import os
import json
import shutil
from pathlib import Path
import click
from jsonschema import validate
import yaml
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

####################
def join_constructor(loader, node):
    """
    Allows FRE properties defined 
    in main yaml to be concatenated.  
    """
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])
####################
def yaml_load(yamlfile):
    """
    Load the given yaml and validate.
    """
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Load the main yaml and validate
    with open(yamlfile,'r') as f:
        y=yaml.load(f,Loader=yaml.Loader)

    return y

####################
def consolidate_yamls(mainyaml,experiment, platform,target):
    """
    Combine main yaml and experiment yaml into combined yamls
    """
    # Path to new combined
    combined=Path("combined.yaml")
    # Create and write to combined yaml
    with open(combined,"w") as f1:
        f1.write('## Combined yamls\n')
        f1.write(f'name: &name "{experiment}"\n')
        f1.write(f'platform: &platform "{platform}"\n')
        f1.write(f'target: &target "{target}"\n\n')

        # Combine main yaml with created combined.yaml
        with open(mainyaml,'r') as f2:
            f1.write("\n### MAIN YAML SETTINGS ###\n")
            #copy contents of main yaml into combined yaml
            shutil.copyfileobj(f2,f1)

    # Load the new combined yaml and validate
    cy=yaml_load(combined)

    # Extract experiment yaml file paths from combined yaml
    exp_list=[]
    for i in cy.get("experiments"):
        exp_list.append(i.get("name"))

    # Check if exp name given is actually valid experiment listed in combined yaml
    if experiment not in exp_list:
        raise Exception(f"{experiment} is not in the list of experiments")

    # Extract specific experiment yaml path for exp. provided
    # if experiment matches name in list of experiments in yaml, extract file path
    for i in cy.get("experiments"):
        if experiment == i.get("name"):
            expyaml=i.get("pp")

    # Combine experiment yaml with combined yaml
    # Could be multiple experiment yamls associated with one experiment
    # expname_list will be used later to set rose-suite items for each ppyaml (needed?)
    expname_list=[]
    if expyaml is not None:
        with open(combined,"a") as f1:
            for i in expyaml:
                expname_list.append(i.split(".")[1])
                with open(i,'r') as f2:
                    f1.write(f"\n### {i.upper()} settings ###\n")
                    #copy expyaml into combined
                    shutil.copyfileobj(f2,f1)
    
    return combined

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
                    rose_suite.set(keys=['template variables', key.upper()], value=f"'{value}'")
    if dirs is not None:
        for key,value in dirs.items():
            rose_suite.set(keys=['template variables', key.upper()], value=f"'{value}'")

####################
def set_rose_apps(yamlfile,rose_regrid,rose_remap):
    """
    Set items in the regrid and remap rose app configurations.
    """
    components = yamlfile.get(f"postprocess").get("components")
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
def _yamlInfo(yamlfile,experiment,platform,target):
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

    # Combine main and exp yamls into one new combine.yaml
    comb_yaml = consolidate_yamls(mainyaml=yml,
                                  experiment=e,
                                  platform=p,
                                  target=t)

    # Load the combined yaml
    final_yaml = yaml_load(comb_yaml)
    
    # Clean combined yaml to validate
    # If keys exists, delete:
    keys_clean=["fre_properties","shared","experiments"]
    for kc in keys_clean:
        if kc in final_yaml.keys():
            del final_yaml[kc]
            
    with open("combined.yaml",'w') as f:
        yaml.safe_dump(final_yaml,f,sort_keys=False)

        # validate yaml
        validate_yaml(final_yaml)


    ## PARSE COMBINED YAML TO CREATE CONFIGS
    # Set rose-suite items
    set_rose_suite(final_yaml,rose_suite)

    # Set regrid and remap rose app items
    set_rose_apps(final_yaml,rose_regrid,rose_remap)

    # write output files
    print("Writing output files...")
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")
    shutil.copyfile(comb_yaml, outfile)
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
def yamlInfo(yamlfile,experiment,platform,target):
    '''
    Wrapper script for calling yamlInfo - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return _yamlInfo(yamlfile,experiment,platform,target)

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
