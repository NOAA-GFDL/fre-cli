"""
CMOR YAML Configuration Generator
=================================

This module powers the ``fre cmor config`` command, generating a CMOR YAML configuration
file that ``fre cmor yaml`` can consume. It scans a post-processing directory tree for
available components and time-series data, cross-references found variables against MIP
tables, and produces the structured YAML needed for CMORization.

Functions
---------
- ``cmor_config_subtool(...)``

.. note:: This module was derived from quick_script.py prototyping work.
"""

import glob
import logging
from pathlib import Path

from .cmor_finder import make_simple_varlist
from .cmor_constants import EXCLUDED_TABLE_SUFFIXES

fre_logger = logging.getLogger(__name__)


def _filter_mip_tables(mip_tables_dir: str, mip_era: str):
    """
    Glob MIP table JSON files from the given directory, filtering out
    non-variable-entry tables (grids, coordinates, etc.).

    :param mip_tables_dir: Path to directory containing MIP table JSON files.
    :type mip_tables_dir: str
    :param mip_era: MIP era string, e.g. 'cmip6' or 'cmip7'.
    :type mip_era: str
    :return: List of paths to MIP table JSON files.
    :rtype: list[str]
    """
    era_upper = mip_era.upper()
    all_tables = glob.glob(f'{mip_tables_dir}/{era_upper}_*.json')

    filtered = []
    for table_path in all_tables:
        table_stem = Path(table_path).stem  # e.g. "CMIP7_ocean"
        suffix = table_stem.split('_', maxsplit=1)[1] if '_' in table_stem else ''
        if suffix not in EXCLUDED_TABLE_SUFFIXES:
            filtered.append(table_path)

    fre_logger.debug('filtered MIP tables (%d of %d): %s',
                     len(filtered), len(all_tables), filtered)
    return filtered


def cmor_config_subtool(
        pp_dir: str,
        mip_tables_dir: str,
        mip_era: str,
        exp_config: str,
        output_yaml: str,
        output_dir: str,
        varlist_dir: str,
        freq: str = 'monthly',
        chunk: str = '5yr',
        grid: str = 'g99',
        overwrite: bool = False,
        calendar_type: str = 'noleap'
):
    """
    Generate a CMOR YAML configuration file from a post-processing directory tree.

    Scans ``pp_dir`` for pp-component directories, cross-references found variables
    against MIP tables, writes per-component variable lists, and emits a structured
    YAML that ``fre cmor yaml`` can later consume.

    :param pp_dir: Root post-processing directory containing per-component subdirectories.
    :type pp_dir: str
    :param mip_tables_dir: Directory containing MIP table JSON files.
    :type mip_tables_dir: str
    :param mip_era: MIP era identifier, e.g. 'cmip6' or 'cmip7'.
    :type mip_era: str
    :param exp_config: Path to JSON experiment/input configuration file expected by CMOR.
    :type exp_config: str
    :param output_yaml: Path to write the output CMOR YAML configuration.
    :type output_yaml: str
    :param output_dir: Root output directory for CMORized data.
    :type output_dir: str
    :param varlist_dir: Directory in which per-component variable list JSON files are written.
    :type varlist_dir: str
    :param freq: Temporal frequency string, e.g. 'monthly', 'daily'. Default 'monthly'.
    :type freq: str
    :param chunk: Time chunk string, e.g. '5yr', '10yr'. Default '5yr'.
    :type chunk: str
    :param grid: Grid label anchor name, e.g. 'g99', 'gn'. Default 'g99'.
    :type grid: str
    :param overwrite: If True, overwrite existing variable list files. Default False.
    :type overwrite: bool
    :param calendar_type: Calendar type string, e.g. 'noleap', '360_day'. Default 'noleap'.
    :type calendar_type: str
    :raises FileNotFoundError: If pp_dir or mip_tables_dir do not exist.
    :raises ValueError: If no MIP tables are found after filtering.
    :return: Path to the written output YAML file.
    :rtype: str
    """
    # ---- validate inputs ----
    if not Path(pp_dir).is_dir():
        raise FileNotFoundError(f'pp_dir does not exist: {pp_dir}')
    if not Path(mip_tables_dir).is_dir():
        raise FileNotFoundError(f'mip_tables_dir does not exist: {mip_tables_dir}')
    if not Path(exp_config).is_file():
        raise FileNotFoundError(f'exp_config does not exist: {exp_config}')

    # ensure output directories exist
    Path(varlist_dir).mkdir(parents=True, exist_ok=True)
    Path(output_yaml).parent.mkdir(parents=True, exist_ok=True)

    # ---- gather MIP tables ----
    mip_tables = _filter_mip_tables(mip_tables_dir, mip_era)
    if not mip_tables:
        raise ValueError(
            f'no MIP tables found in {mip_tables_dir} for era {mip_era} after filtering')

    # ---- discover pp components ----
    ppcompdirs = sorted(glob.glob(f'{pp_dir}/*'))
    fre_logger.info('found %d entries in pp_dir', len(ppcompdirs))

    # ---- build YAML lines ----
    lines = [
        '',
        'cmor:',
        '  start:',
        '    *CMOR_START',
        '  stop:',
        '    *CMOR_STOP',
        '  calendar_type:',
        f"    '{calendar_type}'",
        '  mip_era:',
        f"    '{mip_era}'",
        '  exp_json:',
        f"    '{exp_config}'",
        '  directories:',
        '    pp_dir: &pp_dir',
        f"      '{pp_dir}'",
        '    table_dir: &table_dir',
        f"      '{mip_tables_dir}'",
        '    outdir:',
        f"      '{output_dir}'",
        '  table_targets:',
    ]

    era_upper = mip_era.upper()

    for mip_table in sorted(mip_tables):
        table_name = Path(mip_table).stem.split('.')[0].split('_')[1]   # e.g. CMIP7_ocean
        fre_logger.debug('processing mip_table = %s', table_name)

        appended_table_header = False

        for entry in ppcompdirs:
            component_name = Path(entry).name

            variable_list = f'{varlist_dir}/{era_upper}_{table_name}_{component_name}.list'
            #variable_list = f'{varlist_dir}/{table_name}_{component_name}.list'

            # optionally regenerate
            if Path(variable_list).exists() and overwrite:
                fre_logger.debug('varlist %s exists, unlinking to recreate because overwrite=True',
                                 Path(variable_list).name)
                Path(variable_list).unlink()

            if not Path(entry).is_dir():
                fre_logger.debug('entry %s is not a directory, skipping', entry)
                continue

            # check for time-series data
            data_series_present = [
                Path(ds).name for ds in glob.glob(f'{entry}/*')
                if Path(ds).is_dir()
            ]
            if 'ts' not in data_series_present:
                fre_logger.debug('no ts directory in %s, skipping', entry)
                continue

            dir_targ = f'{entry}/ts/{freq}/{chunk}'
            if not Path(dir_targ).is_dir():
                fre_logger.debug('target dir %s does not exist, skipping', dir_targ)
                continue

            if len(glob.glob(f'{dir_targ}/*nc')) < 1:
                fre_logger.debug('no nc files in %s, skipping', dir_targ)
                continue

            try:
                make_simple_varlist(
                    dir_targ=dir_targ,
                    output_variable_list=variable_list,
                    json_mip_table=mip_table
                )
            except Exception:
                fre_logger.warning(
                    'variable list creation failed for %s %s %s',
                    dir_targ, variable_list, mip_table
                )
                continue

            if Path(variable_list).exists():
                if not appended_table_header:
                    lines.append('')
                    lines.append(f"    - table_name: '{table_name}'")
                    lines.append(f"      freq: '{freq}'")
                    lines.append( '      gridding:')
                    lines.append(f'        <<: *{grid}')
                    lines.append( '      target_components:')
                    appended_table_header = True

                lines.append(f"        - component_name: '{component_name}'")
                lines.append(f"          variable_list: '{variable_list}'")
                lines.append(f"          data_series_type: 'ts'")
                lines.append(f"          chunk: *PP_CMIP_CHUNK")


    # ---- write output YAML ----
    if Path(output_yaml).exists():
        Path(output_yaml).unlink()

    with open(output_yaml, 'w', encoding='utf-8') as out:
        out.write('\n'.join(lines))

    fre_logger.info('wrote CMOR YAML configuration to %s', output_yaml)
    return output_yaml
