"""
CLI Tests for fre workflow *

Tests the command-line-interface commands for each tool in the fre workflow suite.
  - successful invocation of fre workflow $tool 
  - successful invocation of fre workflow $tool --help
  - expected failure for fre workflow $tool --optionDne  (failure for undefined click option)
"""
from pathlib import Path
from click.testing import CliRunner
from fre import fre

runner = CliRunner()

#-- fre workflow
def test_cli_fre_workflow():
    ''' fre workflow '''
    result = runner.invoke(fre.fre, args=["workflow"])
    assert result.exit_code == 2

def test_cli_fre_workflow_help():
    ''' fre workflow --help '''
    result = runner.invoke(fre.fre, args=["workflow", "--help"])
    assert result.exit_code == 0

def test_cli_fre_workflow_opt_dne():
    ''' fre workflow optionDNE '''
    result = runner.invoke(fre.fre, args=["workflow", "optionDNE"])
    assert result.exit_code == 2

#-- fre workflow checkout
def test_cli_fre_workflow_checkout():
    ''' fre workflow checkout'''
    result = runner.invoke(fre.fre, args=["workflow", "checkout"])
    assert result.exit_code == 2

def test_cli_fre_workflow_checkout_help():
    ''' fre workflow checkout --help '''
    result = runner.invoke(fre.fre, args=["workflow", "checkout", "--help"])
    assert result.exit_code == 0

def test_cli_fre_workflow_checkout_opt_dne():
    ''' fre workflow checkout optionDNE '''
    result = runner.invoke(fre.fre, args=["workflow", "checkout", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_workflow_checkout_target_dir_set(tmp_path):
    """
    Test checkout in target directory if --target-dir is explicitly set.
    """
    experiment = "c96L65_am5f7b12r1_amip_TESTING"
    result = runner.invoke(fre.fre, args=["workflow", "checkout",
                                          "--yamlfile", "fre/workflow/tests/AM5_example/am5.yaml",
                                          "--experiment", experiment,
                                          "--application", "pp",
                                          "--target-dir", tmp_path])
    assert result.exit_code == 0
    assert Path(f"{tmp_path}/cylc-src/{experiment}").exists()

def test_cli_fre_workflow_checkout_default_dir(monkeypatch, tmp_path):
    """
    Test workflow repository is cloned in the default location
    if --target-dir is not set; default = ~./fre-workflows
    """
    # Create and set a mock HOME
    fake_home = f"{tmp_path}/fake_home"
    Path(fake_home).mkdir(parents=True,exist_ok=True)
    monkeypatch.setenv("HOME", f"{tmp_path}/fake_home")

    experiment = "c96L65_am5f7b12r1_amip_TESTING"
    result = runner.invoke(fre.fre, args=["workflow", "checkout",
                                          "-y", "fre/workflow/tests/AM5_example/am5.yaml",
                                          "-e", experiment,
                                          "-a", "pp"])
    assert result.exit_code == 0
    assert Path(f"{fake_home}/.fre-workflows/cylc-src/{experiment}").exists()
