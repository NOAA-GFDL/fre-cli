import os
import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from fre import fre

"""
CLI Tests for fre pp *
Tests the command-line-interface calls for tools in the fre pp suite.
Each tool generally gets 3 tests:
    - fre pp $tool, checking for exit code 0 (fails if cli isn't configured right)
    - fre pp $tool --help, checking for exit code 0 (fails if the code doesn't run)
    - fre pp $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured
      right and thinks the tool has a --optionDNE option)
"""

runner = CliRunner()

#-- fre pp
def test_cli_fre_pp():
    ''' fre pp '''
    result = runner.invoke(fre.fre, args=["pp"])
    assert result.exit_code == 2

def test_cli_fre_pp_help():
    ''' fre pp --help '''
    result = runner.invoke(fre.fre, args=["pp", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_opt_dne():
    ''' fre pp optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp checkout
def test_cli_fre_pp_checkout():
    ''' fre pp checkout '''
    result = runner.invoke(fre.fre, args=["pp", "checkout"])
    assert result.exit_code == 2

def test_cli_fre_pp_checkout_help():
    ''' fre pp checkout --help '''
    result = runner.invoke(fre.fre, args=["pp", "checkout", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_checkout_opt_dne():
    ''' fre pp checkout optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "checkout", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_pp_checkout_case():
    ''' fre pp checkout -e FOO -p BAR -t BAZ'''
    directory = os.path.expanduser("~/cylc-src")+'/FOO__BAR__BAZ'
    if Path(directory).exists():
        shutil.rmtree(directory)
    result = runner.invoke(fre.fre, args=["pp", "checkout",
                                          "-e", "FOO",
                                          "-p", "BAR",
                                          "-t", "BAZ"] )
    assert all( [ result.exit_code == 0,
                  Path(directory).exists()] )

#-- fre pp configure-yaml
def test_cli_fre_pp_configure_yaml():
    ''' fre pp configure-yaml '''
    result = runner.invoke(fre.fre, args=["pp", "configure-yaml"])
    assert result.exit_code == 2

def test_cli_fre_pp_configure_yaml_help():
    ''' fre pp configure-yaml --help '''
    result = runner.invoke(fre.fre, args=["pp", "configure-yaml", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_configure_yaml_opt_dne():
    ''' fre pp configure-yaml optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "configure-yaml", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_pp_configure_yaml_fail1():
    ''' fre pp configure-yaml '''
    result = runner.invoke(fre.fre, args = [ "pp", "configure-yaml",
                                             "-e", "FOO",
                                             "-p", "BAR",
                                             "-t", "BAZ",
                                             "-y", "BOO"              ] )
    assert result.exit_code == 1


#-- fre pp install
def test_cli_fre_pp_install():
    ''' fre pp install '''
    result = runner.invoke(fre.fre, args=["pp", "install"])
    assert result.exit_code == 2

def test_cli_fre_pp_install_help():
    ''' fre pp install --help '''
    result = runner.invoke(fre.fre, args=["pp", "install", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_install_opt_dne():
    ''' fre pp install optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "install", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp run
def test_cli_fre_pp_run():
    ''' fre pp run '''
    result = runner.invoke(fre.fre, args=["pp", "run"])
    assert result.exit_code == 2

def test_cli_fre_pp_run_help():
    ''' fre pp run --help '''
    result = runner.invoke(fre.fre, args=["pp", "run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_run_opt_dne():
    ''' fre pp run optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "run", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp status
def test_cli_fre_pp_status():
    ''' fre pp status '''
    result = runner.invoke(fre.fre, args=["pp", "status"])
    assert result.exit_code == 2

def test_cli_fre_pp_status_help():
    ''' fre pp status --help '''
    result = runner.invoke(fre.fre, args=["pp", "status", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_status_opt_dne():
    ''' fre pp status optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "status", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_pp_status_security_check():
    '''
    fre pp status call to make sure the user can't execute nasty, arbitrary commands.
    credit to Utheri Wagura for first pointing this out
    '''
    result = runner.invoke(fre.fre, args=["-vv", "pp", "status",
                                          "-e", ";cat ~/.ssh/id_rsa;",
                                          "-p", ";touch unwanted_file.txt;",
                                          "-t", ";echo $USER;"    ])
    assert not Path('./unwanted_file.txt').exists()
    assert result.exit_code != 0

#-- fre pp validate
def test_cli_fre_pp_validate():
    ''' fre pp validate '''
    result = runner.invoke(fre.fre, args=["pp", "validate"])
    assert result.exit_code == 2

def test_cli_fre_pp_validate_help():
    ''' fre pp validate --help '''
    result = runner.invoke(fre.fre, args=["pp", "validate", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_validate_opt_dne():
    ''' fre pp validate optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "validate", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp wrapper
def test_cli_fre_pp_wrapper():
    ''' fre pp wrapper '''
    result = runner.invoke(fre.fre, args=["pp", "all"])
    assert result.exit_code == 2

def test_cli_fre_pp_wrapper_help():
    ''' fre pp wrapper --help '''
    result = runner.invoke(fre.fre, args=["pp", "all", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_wrapper_opt_dne():
    ''' fre pp wrapper optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "all", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp split-netcdf-wrapper

def test_cli_fre_pp_split_netcdf_wrapper():
    ''' fre pp split-netcdf-wrapper '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf-wrapper"])
    assert result.exit_code == 2

def test_cli_fre_pp_split_netcdf_wrapper_help():
    ''' fre pp split-netcdf-wrapper --help '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf-wrapper", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_split_netcdf_wrapper_opt_dne():
    ''' fre pp split-netcdf-wrapper optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf-wrapper", "optionDNE"])
    assert result.exit_code == 2

#-- fre pp split-netcdf

def test_cli_fre_pp_split_netcdf():
    ''' fre pp split-netcdf '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf"])
    assert result.exit_code == 2

def test_cli_fre_pp_split_netcdf_help():
    ''' fre pp split-netcdf --help '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf", "--help"])
    assert result.exit_code == 0

def test_cli_fre_pp_split_netcdf_opt_dne():
    ''' fre pp split-netcdf optionDNE '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_pp_split_netcdf_rename_help():
    ''' fre pp split-netcdf --help includes --rename option '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf", "--help"])
    assert result.exit_code == 0
    assert "--rename" in result.output

def test_cli_fre_pp_split_netcdf_diag_manifest_help():
    ''' fre pp split-netcdf --help includes --diag-manifest option '''
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf", "--help"])
    assert result.exit_code == 0
    assert "--diag-manifest" in result.output


#-- fre pp split-netcdf --rename (CLI functional tests)

SPLIT_NETCDF_TEST_DIR = os.path.realpath("fre/tests/test_files/ascii_files/split_netcdf")
SPLIT_RENAME_CASES = {
    "ts": {"dir": "atmos_daily.tile3",
           "nc": "00010101.atmos_daily.tile3.nc",
           "cdl": "00010101.atmos_daily.tile3.cdl",
           "component": "atmos_daily"},
    "static": {"dir": "ocean_static",
               "nc": "00010101.ocean_static.nc",
               "cdl": "00010101.ocean_static.cdl",
               "component": "ocean_static"}
}

@pytest.fixture(scope="module")
def split_rename_ncgen():
    '''Generates netcdf files from cdl test data for split --rename CLI tests.'''
    nc_files = []
    for testcase in SPLIT_RENAME_CASES.values():
        cds = os.path.join(SPLIT_NETCDF_TEST_DIR, testcase["dir"])
        nc_path = os.path.join(cds, testcase["nc"])
        cdl_path = os.path.join(cds, testcase["cdl"])
        subprocess.run(["ncgen3", "-k", "netCDF-4", "-o", nc_path, cdl_path],
                       check=True, capture_output=True)
        nc_files.append(nc_path)
    yield nc_files
    for nc in nc_files:
        if os.path.isfile(nc):
            os.unlink(nc)


@pytest.mark.parametrize("case_key", ["ts", "static"])
def test_cli_fre_pp_split_netcdf_rename_run(split_rename_ncgen, tmp_path, case_key):
    ''' fre pp split-netcdf --rename runs successfully via CLI '''
    case = SPLIT_RENAME_CASES[case_key]
    workdir = os.path.join(SPLIT_NETCDF_TEST_DIR, case["dir"])
    infile = os.path.join(workdir, case["nc"])
    outfiledir = str(tmp_path / f"rename_{case_key}")
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf",
                                          "--file", infile,
                                          "--outputdir", outfiledir,
                                          "--variables", "all",
                                          "--rename"])
    assert result.exit_code == 0
    outpath = Path(outfiledir)
    component_dir = outpath / case["component"]
    assert component_dir.is_dir(), f"Expected component directory {component_dir} not found"
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) == 0, f"Flat .nc files remain at root: {root_nc_files}"
    nested_nc_files = list(outpath.rglob("*.nc"))
    assert len(nested_nc_files) > 0, "No .nc files found in nested structure"
    for nc_file in nested_nc_files:
        rel_path = nc_file.relative_to(outpath)
        assert len(rel_path.parts) >= 4, \
            f"File {nc_file} not deep enough: {rel_path.parts}"


def test_cli_fre_pp_split_netcdf_no_rename(split_rename_ncgen, tmp_path):
    ''' fre pp split-netcdf without --rename produces flat output '''
    case = SPLIT_RENAME_CASES["ts"]
    workdir = os.path.join(SPLIT_NETCDF_TEST_DIR, case["dir"])
    infile = os.path.join(workdir, case["nc"])
    outfiledir = str(tmp_path / "no_rename")
    result = runner.invoke(fre.fre, args=["pp", "split-netcdf",
                                          "--file", infile,
                                          "--outputdir", outfiledir,
                                          "--variables", "all"])
    assert result.exit_code == 0
    outpath = Path(outfiledir)
    root_nc_files = list(outpath.glob("*.nc"))
    assert len(root_nc_files) > 0, "No flat .nc files at root without --rename"
    subdirs = [d for d in outpath.iterdir() if d.is_dir()]
    assert len(subdirs) == 0, f"Subdirs created without --rename: {subdirs}"
