"""
Shared fixtures for fre.cmor tests.
"""

from datetime import date
from pathlib import Path
import shutil
import subprocess

import pytest


# ── path constants ──────────────────────────────────────────────────────────
ROOTDIR = Path(__file__).resolve().parent.parent.parent / 'tests' / 'test_files'

CMIP6_TABLE_REPO_PATH = ROOTDIR / 'cmip6-cmor-tables'
CMIP6_TABLE_CONFIG = CMIP6_TABLE_REPO_PATH / 'Tables' / 'CMIP6_Omon.json'

CMIP7_TABLE_REPO_PATH = ROOTDIR / 'cmip7-cmor-tables'
CMIP7_TABLE_CONFIG = CMIP7_TABLE_REPO_PATH / 'tables' / 'CMIP7_ocean.json'

INDIR = ROOTDIR / 'ocean_sos_var_file'
VARLIST = ROOTDIR / 'varlist'
VARLIST_DIFF = ROOTDIR / 'varlist_local_target_vars_differ'
VARLIST_MAPPED = ROOTDIR / 'varlist_mapped'
VARLIST_EMPTY = ROOTDIR / 'empty_varlist'
EXP_CONFIG = ROOTDIR / 'CMOR_input_example.json'
EXP_CONFIG_CMIP7 = ROOTDIR / 'CMOR_CMIP7_input_example.json'

# explicit inputs to tool
GRID = 'regridded to FOO grid from native'
GRID_LABEL = 'gr'
NOM_RES = '10000 km'
CALENDAR_TYPE = 'julian'

# input file details
DATETIMES_INPUTFILE = '199301-199302'
FILENAME_SOS = f'reduced_ocean_monthly_1x1deg.{DATETIMES_INPUTFILE}.sos'
FULL_INPUTFILE = INDIR / f'{FILENAME_SOS}.nc'

FILENAME_SOSV2 = f'reduced_ocean_monthly_1x1deg.{DATETIMES_INPUTFILE}.sosV2.nc'
FULL_INPUTFILE_DIFF = INDIR / FILENAME_SOSV2

FILENAME_MAPPED = f'reduced_ocean_monthly_1x1deg.{DATETIMES_INPUTFILE}.sea_sfc_salinity'
FULL_INPUTFILE_MAPPED = INDIR / f'{FILENAME_MAPPED}.nc'

# determined by cmor_run_subtool for CMIP6 case1
YYYYMMDD = date.today().strftime('%Y%m%d')
CMIP6_CMOR_CREATES_DIR = (
    f'CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/{GRID_LABEL}'
)


# ── ncgen helper ────────────────────────────────────────────────────────────
def _ncgen(cdl_name, nc_path):
    """Run ncgen3 to convert a CDL file into a NetCDF-4 file."""
    cdl_path = ROOTDIR / 'reduced_ascii_files' / cdl_name
    assert cdl_path.exists(), f'CDL file not found: {cdl_path}'

    if nc_path.exists():
        nc_path.unlink()

    subprocess.run(
        ['ncgen3', '-k', 'netCDF-4', '-o', str(nc_path), str(cdl_path)],
        check=True,
    )
    assert nc_path.exists(), f'ncgen3 failed to create {nc_path}'


# ── session-scoped fixtures ─────────────────────────────────────────────────
@pytest.fixture(scope='session')
def cmip6_table_config():
    """Verify CMIP6 table config exists and return its path as a string."""
    assert CMIP6_TABLE_REPO_PATH.exists(), 'CMIP6 table repo not found; run git submodule update --init --recursive'
    assert CMIP6_TABLE_CONFIG.exists(), f'CMIP6 table config not found: {CMIP6_TABLE_CONFIG}'
    return str(CMIP6_TABLE_CONFIG)


@pytest.fixture(scope='session')
def cmip7_table_config():
    """Verify CMIP7 table config exists and return its path as a string."""
    assert CMIP7_TABLE_REPO_PATH.exists(), 'CMIP7 table repo not found; run git submodule update --init --recursive'
    assert CMIP7_TABLE_CONFIG.exists(), f'CMIP7 table config not found: {CMIP7_TABLE_CONFIG}'
    return str(CMIP7_TABLE_CONFIG)


@pytest.fixture(scope='session')
def sos_nc_file():
    """Generate the sos NetCDF file from CDL (session-scoped, created once)."""
    _ncgen(f'{FILENAME_SOS}.cdl', FULL_INPUTFILE)
    return str(FULL_INPUTFILE)


@pytest.fixture(scope='session')
def sosv2_nc_file(sos_nc_file):
    """Create a copy of the sos file as sosV2 (session-scoped)."""
    if not FULL_INPUTFILE_DIFF.exists():
        shutil.copy(Path(sos_nc_file), FULL_INPUTFILE_DIFF)
    assert FULL_INPUTFILE_DIFF.exists()
    return str(FULL_INPUTFILE_DIFF)


@pytest.fixture(scope='session')
def mapped_nc_file():
    """Generate the sea_sfc_salinity NetCDF file from CDL (session-scoped, created once)."""
    _ncgen(f'{FILENAME_MAPPED}.cdl', FULL_INPUTFILE_MAPPED)
    return str(FULL_INPUTFILE_MAPPED)
