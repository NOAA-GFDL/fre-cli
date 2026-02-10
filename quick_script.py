#!/usr/bin/env python3

import getpass
import glob
from pathlib import Path
from pprint import pprint

import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

from fre.cmor.cmor_finder import make_simple_varlist
TEST_PRINT=True

input_exp_config='/home/inl/Working/fre-cli/fre/tests/test_files/CMOR_CMIP7_input_example.json'
output_cmor_yaml_path='/home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/TEST_CMOR_YAML_WRITER_PROTOTYPE.yaml'

chunk='5yr'
freq='monthly'
targdir='/archive/oar.gfdl.bgrp-account/CMIP7/ESM4/DECK/ESM4.5-picontrol/gfdl.ncrc6-intel25-prod-openmp'


input_system='/archive'
input_user='oar.gfdl.bgrp-account'
output_system='/home'
output_user=getpass.getuser()
output_dir=f'{output_system}/{output_user}/Working/fre-cli/ESM45xml/test_cmor_output'
config_dir_out='/home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/variable_lists'
mip_tables_dir='/home/inl/Working/fre-cli/fre/tests/test_files/cmip7-cmor-tables/tables/'
ppcompdirs = glob.glob(f'{targdir}/pp/*')
mip_era='cmip7'
mip_tables=glob.glob(f'{mip_tables_dir}/{mip_era.upper()}_*.json')

lines=[]
lines.append( "")
lines.append(f"cmor:")
lines.append(f"  start:")
lines.append(f"    *CMOR_START")
lines.append(f"  stop:")
lines.append(f"    *CMOR_STOP")
lines.append(f"  calendar_type:")
lines.append(f"    'noleap'")
lines.append(f"  mip_era:")
lines.append(f"    '{mip_era}'")
lines.append(f"  exp_json:")
lines.append(f"    '{input_exp_config}'")
lines.append(f"  directories:")
lines.append(f"    history_dir: !join [{input_system}/{input_user}/, *FRE_STEM, /, *name, /, *platform, -, *target, /, history]")
lines.append(f"    pp_dir: !join [{input_system}/{input_user}/, *FRE_STEM, /, *name, /, *platform, -, *target, /, pp]")
lines.append(f"    table_dir: &table_dir")
lines.append(f"      '{mip_tables_dir}'")
lines.append(f"    outdir:")
lines.append(f"      '{output_dir}'")
lines.append(f"  table_targets:")



for mip_table in mip_tables:
    table_name = str(Path(mip_table).name).split('.')[0].split('_')[1]
    logger.debug(f'doing mip_table = {table_name}')


    for entry in ppcompdirs:
        component_name = Path(entry).name
        
        variable_list = f'{config_dir_out}/CMIP7_{table_name}_{component_name}.list'
        if Path(variable_list).exists():
            Path(variable_list).unlink()

        if not Path(entry).is_dir():
            logger.debug('content of pp-component not a directory, continue')
            continue

        data_series_present = [ Path(found_dataseries).name for found_dataseries in glob.glob(f'{entry}/*') if Path(found_dataseries).is_dir() ]
        if 'ts' not in data_series_present:
            logger.debug('no time-series (ts directory) found in pp-component, continue')
            continue

        dir_targ = f'{entry}/ts/{freq}/{chunk}'
        logger.debug(dir_targ)
        if not Path(dir_targ).is_dir():
            logger.debug('generated target are not a dir / doesnt exist, continue')
            continue

        if len( glob.glob( f'{dir_targ}/*nc' ) ) < 1:
            logger.debug('directory target has no files ending in *nc, continue')
            continue
            
        try:
            make_simple_varlist( dir_targ = dir_targ,
                                 output_variable_list = variable_list,
                                 json_mip_table = mip_table )
        except:
            logger.warning(f'variable list creation FAILED for %s %s %s', dir_targ,variable_list,mip_table)
            pass
                
        if Path(variable_list).exists():
            lines.append( "")
            lines.append(f"    - table_name: '{table_name}'")
            lines.append( "      variable_list:")
            lines.append(f"        '{variable_list}'")
            lines.append( "      freq: 'monthly'")
            lines.append( "      gridding:")
            lines.append( "        <<: *g99")
            lines.append( "      target_components:")
            lines.append(f"        - componment_name: '{Path(entry).name}'")
            lines.append(f"          data_series_type: 'ts'")
            lines.append(f"          chunk: *PP_CMIP_CHUNK")



if TEST_PRINT:
    pprint(lines)

if Path(output_cmor_yaml_path).exists():
    Path(output_cmor_yaml_path).unlink()

with open(output_cmor_yaml_path, 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines))
