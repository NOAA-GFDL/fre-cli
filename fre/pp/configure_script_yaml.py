#!/usr/bin/env python
"""
    Script creates rose-apps and rose-suite
    files for the workflow from the pp yaml.
"""

import os
import json
import shutil
from pathlib import Path
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
def yamlload(yamlfile):
    """
    Load the given yaml and validate.
    """
    # Regsiter tag handler
    yaml.add_constructor('!join', join_constructor)

    # Load the main yaml and validate
    with open(yamlfile,'r') as f:
        y=yaml.load(f,Loader=yaml.Loader)
        #validate_yaml(y)

## TO-DO:
# - figure out way to safe_load (yaml_loader=yaml.SafeLoader?)
# - update validation and schema
    return y

####################
def consolidate_yamls(yamlfile,experiment, platform,target):
    """
    Combine main yaml and experiment yaml into combined yamls
    """
    # Path to new combined
    combined=Path("combined.yaml")
    # Create and write to combined yaml
    with open(combined,"w") as f1:
        f1.write('## Combined yamls\n')
        f1.write(f'define: &name "{experiment}"\n')
        f1.write(f'define: &platform "{platform}"\n')
        f1.write(f'define: &target "{target}"\n\n')

        # Combine main yaml with
        with open(yamlfile,'r') as f2:
            f1.write("\n### MAIN YAML SETTINGS ###\n")
            shutil.copyfileobj(f2,f1)  #copy contents of main yaml into combined yaml

    # Load the new combined yaml and validate
    cy=yamlload(combined)

    # Extract the experiment yaml
    exp_list=[]
    for i in cy.get("experiments"):
        exp_list.append(i.get("name"))

    # Check is exp name is valid experiment listed in main yaml
    if experiment not in exp_list:
        raise Exception(f"{experiment} is not in the list of experiments")

    for i in cy.get("experiments"):
        # Extract the experiment yaml
        if experiment == i.get("name"):
            expyaml=i.get("pp")
        #else:
        # simplify combine yaml?: remove name,ppyamls if it doesnt match experiment given
        #remove i.get("name") and i.get("pp") associated with it

    if expyaml is not None:
        #combine experiment yaml with combined yaml
        with open(combined,"a") as f1:
            for i in expyaml:
                with open(i,'r') as f2: #copy expyaml into combined
                    f1.write(f"\n### {i.upper()} settings ###\n")
                    shutil.copyfileobj(f2,f1)

## TO-DO: 
# - condition where there are multiple pp yamls

    return combined

####################
#def clean():
#    """
#    """
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

    # initialize rose suite config
    rose_suite = metomi.rose.config.ConfigNode()
    #rose_suite.set(keys=['template variables', 'SITE'],              value='"ppan"')
    #rose_suite.set(keys=['template variables', 'CLEAN_WORK'],        value='True')
    #rose_suite.set(keys=['template variables', 'PTMP_DIR'],          value='"/xtmp/$USER/ptmp"')
    #rose_suite.set(keys=['template variables', 'DO_STATICS'],        value='True')
    #rose_suite.set(keys=['template variables', 'DO_TIMEAVGS'],       value='True')
    #rose_suite.set(keys=['template variables', 'DO_ATMOS_PLEVEL_MASKING'], value='True')
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

    # Combine main and exp yamls into one new combine.yaml
    comb_yaml = consolidate_yamls(yamlfile=yml,
                                  experiment=e,
                                  platform=p,
                                  target=t)

    # Load the combined yaml
    YAML = yamlload(comb_yaml)

    ## PARSE COMBINED YAML TO CREATE CONFIGS
    # Remove unwanted keys
    del YAML["experiments"]
    del YAML["define"]

    for i in YAML.keys():
        #print(i)
        if YAML.get(i) is not None:
            for configkey,configvalue in YAML.get(i).items():
                if isinstance(configvalue,dict):  ##for settings and switches
                    for i,j in configvalue.items():
                        rose_suite.set(keys=['template variables', i.upper()], value=f'{j}')
                elif isinstance(configvalue,str): ##for directories
                    rose_suite.set(keys=['template variables', configkey.upper()],
                                   value=f'{configvalue}')

    components = YAML.get("postprocess").get("components")
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
            print(i.values())
            rose_regrid.set(keys=[f'{comp}', 'sources'], value=f'{sources}')
            rose_regrid.set(keys=[f'{comp}', 'inputRealm'], value=f'{i.get("inputRealm")}')
            rose_regrid.set(keys=[f'{comp}', 'inputGrid'], value=f'{i.get("sourceGrid")}')
            rose_regrid.set(keys=[f'{comp}', 'interpMethod'], value=f'{interp_method}')
            interp_split = i.get('xyInterp').split(',')
            rose_regrid.set(keys=[f'{comp}', 'outputGridLon'], value=f'{interp_split[1]}')
            rose_regrid.set(keys=[f'{comp}', 'outputGridLat'], value=f'{interp_split[0]}')
            rose_regrid.set(keys=[f'{comp}', 'outputGridType'],
                            value=f'{interp_split[0]}_{interp_split[1]}.{interp_method}')

    # write output files
    print("Writing output files...")
    cylc_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{e}__{p}__{t}")
    outfile = os.path.join(cylc_dir, f"{e}.yaml")
    shutil.copyfile(YAML, outfile)
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

def yamlInfo(yamlfile,experiment,platform,target):
    '''
    Wrapper script for calling yamlInfo - allows the decorated version
    of the function to be separate from the undecorated version
    '''
    return _yamlInfo(yamlfile,experiment,platform,target)

# Use parseyaml function to parse created edits.yaml
if __name__ == '__main__':
    yamlInfo()
