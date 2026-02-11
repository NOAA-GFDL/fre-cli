"""
a different approach to configuring a workload/workflow for fre.cmor

prototype command module, cmor_writer, cli call 'fre cmor write'
"""

import getpass
import glob
from pathlib import Path
from pprint import pprint, pformat

import logging

from fre.cmor.cmor_finder import make_simple_varlist

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

TEST_PRINT=False
logger.debug('TEST_PRINT=%s',TEST_PRINT)
REMAKE_LISTS=True
logger.debug('REMAKE_LISTS=%s',REMAKE_LISTS)

input_system='/archive'
input_user='oar.gfdl.bgrp-account'
chunk='5yr'
freq='monthly'
grid='g99'
targdir='/archive/oar.gfdl.bgrp-account/CMIP7/ESM4/DECK/ESM4.5-picontrol/gfdl.ncrc6-intel25-prod-openmp'


output_cmor_yaml_path='/home/inl/Working/ESM45xml/yaml_workflow/esm45-v14/test_cmor_yaml_writer_prototype.yaml'
#output_system='/home'
#output_system='/net'
output_system='/net2'
output_user=getpass.getuser()
output_dir=f'{output_system}/{output_user}/Working/fre-cli/ESM45xml/test_cmor_output'
config_dir_out=f'/home/{output_user}/Working/ESM45xml/yaml_workflow/esm45-v14/variable_lists'
ppcompdirs = glob.glob(f'{targdir}/pp/*')

input_exp_config='/home/inl/Working/fre-cli/fre/tests/test_files/CMOR_CMIP7_input_example.json'
mip_tables_dir=f'/home/{output_user}/Working/fre-cli/fre/tests/test_files/cmip7-cmor-tables/tables'
mip_era='cmip7'
mip_tables=glob.glob(f'{mip_tables_dir}/{mip_era.upper()}_*.json')
logger.debug('mip_tables = \n %s', pformat(mip_tables))
def try_remove_except_pass(input_list, entry_to_remove):
    '''
    tries to remove an element from a list based on exact match.
    
    if it can't, s'ok... move on.
    '''
    logger.info('trying to remove unnecessary mip table entries')
    logger.debug('entry to remove is: %s', entry_to_remove)
    try:
        input_list.remove(entry_to_remove)
    except:
        logger.warning('couldnt remove, nbd, move on')
try_remove_except_pass(mip_tables, f'{mip_tables_dir}/{mip_era.upper()}_long_name_overrides.json')
try_remove_except_pass(mip_tables, f'{mip_tables_dir}/{mip_era.upper()}_grids.json')
try_remove_except_pass(mip_tables, f'{mip_tables_dir}/{mip_era.upper()}_formula_terms.json')
try_remove_except_pass(mip_tables, f'{mip_tables_dir}/{mip_era.upper()}_coordinate.json')
try_remove_except_pass(mip_tables, f'{mip_tables_dir}/{mip_era.upper()}_cell_measures.json')

assert False

logger.debug('appending initial lines to CMOR yaml')
lines=[]
lines.append( "")
lines.append( "cmor:")
lines.append( "  start:")
lines.append( "    *CMOR_START")
lines.append( "  stop:")
lines.append( "    *CMOR_STOP")
lines.append( "  calendar_type:")
lines.append( "    'noleap'")
lines.append( "  mip_era:")
lines.append(f"    '{mip_era}'")
lines.append( "  exp_json:")
lines.append(f"    '{input_exp_config}'")
lines.append( "  directories:")
lines.append(f"    history_dir: !join [{input_system}/{input_user}/, *FRE_STEM, /, *name, /, *platform, -, *target, /, history]")
lines.append(f"    pp_dir: !join [{input_system}/{input_user}/, *FRE_STEM, /, *name, /, *platform, -, *target, /, pp]")
lines.append( "    table_dir: &table_dir")
lines.append(f"      '{mip_tables_dir}'")
lines.append( "    outdir:")
lines.append(f"      '{output_dir}'")
lines.append( "  table_targets:")


logger.debug('starting loop over %s mip_tables targets', len(mip_tables))
for mip_table in mip_tables:
    #table_name = str(Path(mip_table).name).split('.')[0].split('_')[1]
    table_name = str(Path(mip_table).name).split('.', maxsplit=1)[0]
    logger.debug(f'doing mip_table = {table_name}')

    appended_table_header=False
    logger.debug('starting loop over %s ppcompdirs targets', len(ppcompdirs))
    for entry in ppcompdirs:
        component_name = Path(entry).name

        variable_list = f'{config_dir_out}/CMIP7_{table_name}_{component_name}.list'
        if Path(variable_list).exists():
            if REMAKE_LISTS:
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

            if not appended_table_header:
                lines.append( "")
                lines.append(f"    - table_name: '{table_name}'")
                lines.append(f"      freq: '{freq}'")
                lines.append( "      gridding:")
                lines.append(f"        <<: *{grid}")
                lines.append( "      target_components:")
                appended_table_header=True

            lines.append(f"        - component_name: '{component_name}'")
            lines.append(f"          variable_list: '{variable_list}'")
            lines.append(f"          data_series_type: 'ts'")
            lines.append(f"          chunk: *PP_CMIP_CHUNK")



if TEST_PRINT:
    pprint(lines)

if Path(output_cmor_yaml_path).exists():
    Path(output_cmor_yaml_path).unlink()

with open(output_cmor_yaml_path, 'w', encoding='utf-8') as out:
    out.write('\n'.join(lines))
