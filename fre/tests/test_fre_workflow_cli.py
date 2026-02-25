"""
CLI Tests for fre workflow *
Tests the command-line-interface calls for tools in the fre workflow suite.

Each tool generally gets 3 tests:
  - fre workflow $tool, checking for exit code 0 (fails if cli isn't configured right)
  - fre workflow $tool --help, checking for exit code 0 (fails if the code doesn't run)
  - fre workflow $tool --optionDNE, checking for exit code 2; misuse of command (fails if cli isn't configured
    right and thinks the tool has a --optionDNE option)
"""
import os
from pathlib import Path
from click.testing import CliRunner
from fre import fre

runner = CliRunner()

## fre workflow subtools search for if TMPDIR is set, specifically for fre workflow checkout --target-dir
# If a value for --target-dir is not passed --> TMPDIR will be used for --target-dir
# If TMPDIR is not set --> a default location will be used for --target-dir 
#-- fre workflow
def test_cli_fre_workflow(monkeypatch):
    ''' fre workflow '''
    monkeypatch.setenv("TMPDIR", "")
    result = runner.invoke(fre.fre, args=["workflow"])
    assert result.exit_code == 0

def test_cli_fre_workflow_help(monkeypatch):
    ''' fre workflow --help '''
    monkeypatch.setenv("TMPDIR", "")
    result = runner.invoke(fre.fre, args=["workflow", "--help"])
    assert result.exit_code == 0

def test_cli_fre_workflow_opt_dne(monkeypatch):
    ''' fre workflow optionDNE '''
    monkeypatch.setenv("TMPDIR", "")
    result = runner.invoke(fre.fre, args=["workflow", "optionDNE"])
    assert result.exit_code == 2

#-- fre workflow checkout
def test_cli_fre_workflow_checkout(monkeypatch):
    ''' fre workflow checkout'''
    monkeypatch.setenv("TMPDIR", "")
    result = runner.invoke(fre.fre, args=["workflow", "checkout"])
    assert result.exit_code == 2

def test_cli_fre_workflow_checkout_help(monkeypatch):
    ''' fre workflow checkout --help '''
    monkeypatch.setenv("TMPDIR", "")
    result = runner.invoke(fre.fre, args=["workflow", "checkout", "--help"])
    assert result.exit_code == 0

def test_cli_fre_workflow_checkout_opt_dne(monkeypatch):
    ''' fre workflow checkout optionDNE '''
    monkeypatch.setenv("TMPDIR", "")
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

def test_cli_fre_workflow_checkout_TMPDIR_set(tmp_path, monkeypatch):
    """
    Test checkout if TMPDIR environment variable is set and --target-dir has no
    specified value
    """
    experiment = "c96L65_am5f7b12r1_amip_TESTING"
    Path(f"{tmp_path}/env_var").mkdir(parents=True)
    monkeypatch.setenv("TMPDIR", f"{tmp_path}/env_var")
    
    result = runner.invoke(fre.fre, args=["workflow", "checkout",
                                          "-y", "fre/workflow/tests/AM5_example/am5.yaml",
                                          "-e", experiment,
                                          "-a", "pp"])
    assert result.exit_code == 0
    assert Path(f"{os.environ['TMPDIR']}/cylc-src/{experiment}").exists()

#def test_cli_fre_workflow_checkout_default_dir():
#    """
#    Test checkout if TMPDIR and --target-dir is not set;
#    use the default location: ~/.fre
#    """
    experiment = "c96L65_am5f7b12r1_amip_TESTING"
    monkeypatch.setenv("TMPDIR", "")

    result = runner.invoke(fre.fre, args=["workflow", "checkout",
                                          "-y", "fre/workflow/tests/AM5_example/am5.yaml",
                                          "-e", experiment,
                                          "-a", "pp"])
    #default cylc-src location
    default_dir = os.path.expanduser("~/.fre")
    assert result.exit_code == 0
    assert Path(f"{default_dir}/cylc-src/{experiment}").exists()
