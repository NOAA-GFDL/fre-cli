import os
import shutil
from pathlib import Path

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
    assert result.exit_code == 0

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
