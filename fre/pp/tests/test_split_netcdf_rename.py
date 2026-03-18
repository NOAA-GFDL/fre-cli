'''
Tests split-netcdf with --rename flag.
Tests the combined split + rename functionality that reorganizes
split netcdf files into a nested directory structure with frequency and duration.

Uses the existing split-netcdf test data (atmos_daily, ocean_static) to verify
the --rename flag behavior via both CLI (CliRunner) and direct import.
'''

import pytest
import re
import subprocess
import os
from os import path as osp
import pathlib
from pathlib import Path
from fre import fre
from fre.pp import split_netcdf_script
from fre.pp import rename_split_script

import click
from click.testing import CliRunner
runner = CliRunner()

test_dir = osp.realpath("fre/tests/test_files/ascii_files/split_netcdf")

cases = {"ts": {"dir": "atmos_daily.tile3",
                "nc": "00010101.atmos_daily.tile3.nc",
                "cdl": "00010101.atmos_daily.tile3.cdl"},
         "static": {"dir": "ocean_static",
                     "nc": "00010101.ocean_static.nc",
                     "cdl": "00010101.ocean_static.cdl"}}

casedirs = [osp.join(test_dir, el) for el in [cases["ts"]["dir"], cases["static"]["dir"]]]

rename_outdir_prefix = "new_rename_"


def test_split_rename_setup():
    '''Sets up the netcdf files needed for split+rename testing.'''
    ncgen_commands = []
    sp_stat = []
    for testcase in cases.keys():
        cds = osp.join(test_dir, cases[testcase]["dir"])
        ncgen_commands.append(["ncgen3", "-k", "netCDF-4", "-o",
                               osp.join(cds, cases[testcase]["nc"]),
                               osp.join(cds, cases[testcase]["cdl"])])
    for ncg in ncgen_commands:
        sp = subprocess.run(ncg, check=True, capture_output=True)
        sp_stat.append(sp.returncode)
    sp_success = [el == 0 for el in sp_stat]
    assert all(sp_success)


@pytest.mark.parametrize("workdir,infile,outfiledir,varlist",
                         [pytest.param(casedirs[0], cases["ts"]["nc"],
                                       rename_outdir_prefix + "ts_all", "all",
                                       id="rename_ts_all"),
                          pytest.param(casedirs[1], cases["static"]["nc"],
                                       rename_outdir_prefix + "static_all", "all",
                                       id="rename_static_all")])
def test_split_rename_cli_run(workdir, infile, outfiledir, varlist):
    '''Tests split-netcdf with --rename flag via CLI CliRunner.

    Verifies that the command exits successfully when --rename is used.
    '''
    infile = osp.join(workdir, infile)
    outfiledir = osp.join(workdir, outfiledir)
    split_netcdf_args = ["pp", "split-netcdf",
                         "--file", infile,
                         "--outputdir", outfiledir,
                         "--variables", varlist,
                         "--rename"]
    result = runner.invoke(fre.fre, args=split_netcdf_args)
    print(result.output)
    if result.exception:
        import traceback
        traceback.print_exception(type(result.exception), result.exception, result.exception.__traceback__)
    assert result.exit_code == 0


@pytest.mark.parametrize("workdir,outfiledir,expected_component",
                         [pytest.param(casedirs[0],
                                       rename_outdir_prefix + "ts_all",
                                       "atmos_daily",
                                       id="rename_ts_structure"),
                          pytest.param(casedirs[1],
                                       rename_outdir_prefix + "static_all",
                                       "ocean_static",
                                       id="rename_static_structure")])
def test_split_rename_cli_structure(workdir, outfiledir, expected_component):
    '''Verifies that split+rename created the expected nested directory structure.

    After split+rename:
    - Timeseries: outputdir/component/freq/duration/component.date1-date2.var.tile.nc
    - Static: outputdir/component/P0Y/P0Y/component.var.nc

    Also verifies no flat .nc files remain at the root of outputdir.
    '''
    outfiledir = osp.join(workdir, outfiledir)
    outpath = Path(outfiledir)

    # Check that the component directory was created
    component_dir = outpath / expected_component
    assert component_dir.is_dir(), f"Expected component directory {component_dir} not found"

    # Check that no flat .nc files remain at the root of outfiledir
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) == 0, f"Flat .nc files remain at root: {root_nc_files}"

    # Check that .nc files exist somewhere in the nested structure
    nested_nc_files = list(outpath.rglob("*.nc"))
    assert len(nested_nc_files) > 0, "No .nc files found in nested structure"


@pytest.mark.parametrize("workdir,outfiledir",
                         [pytest.param(casedirs[0],
                                       rename_outdir_prefix + "ts_all",
                                       id="rename_ts_freq"),
                          pytest.param(casedirs[1],
                                       rename_outdir_prefix + "static_all",
                                       id="rename_static_freq")])
def test_split_rename_cli_freq_dirs(workdir, outfiledir):
    '''Verifies that split+rename created frequency and duration subdirectories.

    For timeseries (atmos_daily), expects freq/duration dirs (e.g. P1D/P6M)
    For static (ocean_static), expects P0Y/P0Y
    '''
    outfiledir = osp.join(workdir, outfiledir)
    outpath = Path(outfiledir)

    # Find all .nc files
    nc_files = list(outpath.rglob("*.nc"))
    assert len(nc_files) > 0

    # Check that each .nc file is at least 3 levels deep
    # (component/freq/duration/file.nc)
    for nc_file in nc_files:
        rel_path = nc_file.relative_to(outpath)
        parts = rel_path.parts
        assert len(parts) >= 4, \
            f"File {nc_file} is not deep enough: {parts}"


def test_split_rename_import_run():
    '''Tests split+rename via direct import (standard import path).

    Uses split_file_xarray + rename_file + link_or_copy directly.
    '''
    workdir = casedirs[0]
    infile_name = cases["ts"]["nc"]
    infile = osp.join(workdir, infile_name)
    outfiledir = osp.join(workdir, rename_outdir_prefix + "import_ts")

    # Split the file
    split_netcdf_script.split_file_xarray(infile, outfiledir, "all")

    # Rename the split files
    outpath = Path(outfiledir)
    basename = Path(infile).stem
    pattern = f"{basename}.*.nc"
    split_files = list(outpath.glob(pattern))
    assert len(split_files) > 0, "No split files were created"

    for split_file in split_files:
        new_rel_path = rename_split_script.rename_file(split_file)
        new_full_path = outpath / new_rel_path
        rename_split_script.link_or_copy(str(split_file), str(new_full_path))
        split_file.unlink()

    # Verify no flat .nc files remain at root
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) == 0, f"Flat .nc files remain at root: {root_nc_files}"

    # Verify nested structure was created
    nested_nc_files = list(outpath.rglob("*.nc"))
    assert len(nested_nc_files) > 0, "No .nc files found in nested structure"

    # Verify component directory
    component_dir = outpath / "atmos_daily"
    assert component_dir.is_dir(), f"Component directory {component_dir} not found"


def test_split_rename_without_flag():
    '''Tests that split-netcdf without --rename produces flat output (no nesting).

    This verifies backward compatibility.
    '''
    workdir = casedirs[0]
    infile_name = cases["ts"]["nc"]
    infile = osp.join(workdir, infile_name)
    outfiledir = osp.join(workdir, rename_outdir_prefix + "no_rename")

    split_netcdf_args = ["pp", "split-netcdf",
                         "--file", infile,
                         "--outputdir", outfiledir,
                         "--variables", "all"]
    result = runner.invoke(fre.fre, args=split_netcdf_args)
    assert result.exit_code == 0

    outpath = Path(outfiledir)
    # Verify flat .nc files exist at root (no nesting)
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) > 0, "No flat .nc files at root without --rename"

    # Verify no subdirectories were created
    subdirs = [d for d in outpath.iterdir() if d.is_dir()]
    assert len(subdirs) == 0, f"Subdirs created without --rename: {subdirs}"


def test_split_rename_cleanup():
    '''Cleans up files and dirs created for split+rename tests.'''
    el_list = []
    dir_list = []
    for path, subdirs, files in os.walk(test_dir):
        for name in files:
            if name.endswith(".nc"):
                el_list.append(osp.join(path, name))
        for name in subdirs:
            if name.startswith(rename_outdir_prefix):
                dir_list.append(osp.join(path, name))
    for nc in el_list:
        pathlib.Path.unlink(Path(nc))
    # Sort in reverse to delete deepest dirs first
    all_dirs = []
    for d in dir_list:
        for path, subdirs, files in os.walk(d, topdown=False):
            all_dirs.append(path)
    for d in sorted(all_dirs, reverse=True):
        if osp.isdir(d):
            pathlib.Path.rmdir(Path(d))
    dir_deleted = [not osp.isdir(el) for el in dir_list]
    el_deleted = [not osp.isfile(el) for el in el_list]
    assert all(el_deleted + dir_deleted)
