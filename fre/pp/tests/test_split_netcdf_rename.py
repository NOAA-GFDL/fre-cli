'''
Tests split-netcdf with --rename flag.
Tests the combined split + rename functionality that reorganizes
split netcdf files into a nested directory structure with frequency and duration.

Uses the existing split-netcdf test data (atmos_daily, ocean_static) to verify
the --rename flag behavior via direct import.
CLI tests (CliRunner) are in fre/tests/test_fre_pp_cli.py.
'''

import pytest
import subprocess
import os
from os import path as osp
import shutil
from pathlib import Path
from fre.pp import split_netcdf_script
from fre.pp import rename_split_script

test_dir = osp.realpath("fre/tests/test_files/ascii_files/split_netcdf")

cases = {"ts": {"dir": "atmos_daily.tile3",
                "nc": "00010101.atmos_daily.tile3.nc",
                "cdl": "00010101.atmos_daily.tile3.cdl"},
         "static": {"dir": "ocean_static",
                     "nc": "00010101.ocean_static.nc",
                     "cdl": "00010101.ocean_static.cdl"}}

# scope=module means that this is invoked once for the tests that run from this file
@pytest.fixture(scope="module")
def ncgen_setup():
    '''Generates netcdf files from cdl test data needed for split+rename testing.'''
    nc_files = []
    for testcase in cases.keys():
        cds = osp.join(test_dir, cases[testcase]["dir"])
        nc_path = osp.join(cds, cases[testcase]["nc"])
        cdl_path = osp.join(cds, cases[testcase]["cdl"])
        subprocess.run(["ncgen3", "-k", "netCDF-4", "-o", nc_path, cdl_path],
                       check=True, capture_output=True)
        nc_files.append(nc_path)
    yield nc_files
    for nc in nc_files:
        if osp.isfile(nc):
            os.unlink(nc)


def test_split_rename_import_ts(ncgen_setup, tmp_path):
    '''Tests split+rename via direct import for timeseries data.

    Uses split_file_xarray with rename=True directly.
    '''
    workdir = osp.join(test_dir, cases["ts"]["dir"])
    infile = osp.join(workdir, cases["ts"]["nc"])
    outfiledir = str(tmp_path / "import_ts")

    split_netcdf_script.split_file_xarray(infile, outfiledir, "all",
                                          rename=True)

    outpath = Path(outfiledir)

    # Verify no flat .nc files remain at root
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) == 0, f"Flat .nc files remain at root: {root_nc_files}"

    # Verify nested structure was created
    nested_nc_files = list(outpath.rglob("*.nc"))
    assert len(nested_nc_files) > 0, "No .nc files found in nested structure"

    # Verify component directory
    component_dir = outpath / "atmos_daily"
    assert component_dir.is_dir(), f"Component directory {component_dir} not found"

    # Verify depth (component/freq/duration/file.nc)
    for nc_file in nested_nc_files:
        rel_path = nc_file.relative_to(outpath)
        parts = rel_path.parts
        assert len(parts) >= 4, \
            f"File {nc_file} is not deep enough: {parts}"


def test_split_rename_import_static(ncgen_setup, tmp_path):
    '''Tests split+rename via direct import for static data.

    Uses split_file_xarray with rename=True directly.
    '''
    workdir = osp.join(test_dir, cases["static"]["dir"])
    infile = osp.join(workdir, cases["static"]["nc"])
    outfiledir = str(tmp_path / "import_static")

    split_netcdf_script.split_file_xarray(infile, outfiledir, "all",
                                          rename=True)

    outpath = Path(outfiledir)

    # Verify no flat .nc files remain at root
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) == 0, f"Flat .nc files remain at root: {root_nc_files}"

    # Verify nested structure was created
    nested_nc_files = list(outpath.rglob("*.nc"))
    assert len(nested_nc_files) > 0, "No .nc files found in nested structure"

    # Verify component directory
    component_dir = outpath / "ocean_static"
    assert component_dir.is_dir(), f"Component directory {component_dir} not found"

    # Verify depth (component/P0Y/P0Y/file.nc)
    for nc_file in nested_nc_files:
        rel_path = nc_file.relative_to(outpath)
        parts = rel_path.parts
        assert len(parts) >= 4, \
            f"File {nc_file} is not deep enough: {parts}"


def test_split_rename_without_flag(ncgen_setup, tmp_path):
    '''Tests that split_file_xarray without rename produces flat output (no nesting).

    This verifies backward compatibility.
    '''
    workdir = osp.join(test_dir, cases["ts"]["dir"])
    infile = osp.join(workdir, cases["ts"]["nc"])
    outfiledir = str(tmp_path / "no_rename")

    split_netcdf_script.split_file_xarray(infile, outfiledir, "all")

    outpath = Path(outfiledir)
    # Verify flat .nc files exist at root (no nesting)
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) > 0, "No flat .nc files at root without rename"

    # Verify no subdirectories were created
    subdirs = [d for d in outpath.iterdir() if d.is_dir()]
    assert len(subdirs) == 0, f"Subdirs created without rename: {subdirs}"

