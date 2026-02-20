import os
import shutil
from pathlib import Path

from click.testing import CliRunner

from fre import fre

"""
CLI Tests for fre workflow *
Tests the command-line-interface calls for tools in the fre workflow suite.
Each tool generally gets 3 tests:
    - fre workflow $tool, checking for exit code 0 (fails if cli isn't configured right)
    - fre workflow $tool --help, checking for exit code 0 (fails if the code doesn't run)
    - fre workflow $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured
      right and thinks the tool has a --optionDNE option)
"""

runner = CliRunner()

#-- fre pp
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

