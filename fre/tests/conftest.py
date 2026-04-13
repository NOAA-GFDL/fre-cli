"""
Shared fixtures for fre/tests CLI integration tests.
"""

from datetime import date
from pathlib import Path
import shutil
import subprocess

import pytest

from fre import fre


# ── path constants ──────────────────────────────────────────────────────────
ROOTDIR = Path(fre.__file__).parent / 'tests' / 'test_files'

CMIP6_TABLE_CONFIG = ROOTDIR / 'cmip6-cmor-tables' / 'Tables' / 'CMIP6_Omon.json'
CMIP7_TABLE_CONFIG = ROOTDIR / 'cmip7-cmor-tables' / 'tables' / 'CMIP7_ocean.json'

INDIR = ROOTDIR / 'ocean_sos_var_file'
VARLIST = ROOTDIR / 'varlist'
VARLIST_DIFF = ROOTDIR / 'varlist_local_target_vars_differ'
VARLIST_MAPPED = ROOTDIR / 'varlist_mapped'
EXP_CONFIG = ROOTDIR / 'CMOR_input_example.json'
EXP_CONFIG_CMIP7 = ROOTDIR / 'CMOR_CMIP7_input_example.json'

SOS_NC_FILENAME = 'reduced_ocean_monthly_1x1deg.199301-199302.sos.nc'
SOSV2_NC_FILENAME = 'reduced_ocean_monthly_1x1deg.199301-199302.sosV2.nc'
MAPPED_NC_FILENAME = 'reduced_ocean_monthly_1x1deg.199301-199302.sea_sfc_salinity.nc'

YYYYMMDD = date.today().strftime('%Y%m%d')


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
def cli_sos_nc_file():
    """Generate the sos NetCDF file from CDL (session-scoped)."""
    nc_path = INDIR / SOS_NC_FILENAME
    _ncgen('reduced_ocean_monthly_1x1deg.199301-199302.sos.cdl', nc_path)
    return str(nc_path)


@pytest.fixture(scope='session')
def cli_sosv2_nc_file(cli_sos_nc_file):
    """Create a copy of the sos file as sosV2 (session-scoped)."""
    nc_path = INDIR / SOSV2_NC_FILENAME
    if nc_path.exists():
        nc_path.unlink()
    shutil.copy(cli_sos_nc_file, str(nc_path))
    assert nc_path.exists()
    return str(nc_path)


@pytest.fixture(scope='session')
def cli_mapped_nc_file():
    """Generate the sea_sfc_salinity NetCDF file from CDL (session-scoped)."""
    nc_path = INDIR / MAPPED_NC_FILENAME
    _ncgen('reduced_ocean_monthly_1x1deg.199301-199302.sea_sfc_salinity.cdl', nc_path)
    return str(nc_path)
