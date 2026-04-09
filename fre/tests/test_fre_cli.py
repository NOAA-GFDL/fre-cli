"""
CLI Tests for fre

Tests the command-line-interface calls for fre itself. 
We've got 4-ish tests:

- fre , checking for exit code 0 (fails if cli isn't configured right)
- fre --help, checking for exit code 0 (fails if the code doesn't run)
- fre --optionDNE, checking for exit code 2 (fails if cli isn't configured 
  right and thinks the tool has a --optionDNE option)
- fre --version, checking for version GTE current version (fails if version isn't defined)
"""
import sys
import subprocess
from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre():
    ''' fre '''
    result = runner.invoke(fre.fre)
    assert result.exit_code == 2

def test_cli_fre_help():
    ''' fre --help '''
    result = runner.invoke(fre.fre, args='--help')
    assert result.exit_code == 0

def test_cli_fre_option_dne():
    ''' fre optionDNE '''
    result = runner.invoke(fre.fre, args='optionDNE')
    assert result.exit_code == 2


def test_fre_version():
    ''' module import flavor of below cli test '''
    assert '2026.01.alpha2' == fre.version

def test_cli_fre_version():
    ''' fre --version '''
    result = runner.invoke(fre.fre, args='--version')
    expected_out = 'fre, version 2026.01.alpha2'
    assert all( [ result.exit_code == 0,
                  expected_out in result.output ] )

#def test_fre_version_testing_tag():
#    ''' module import flavor of below cli test '''
#    result = subprocess.run(["git", "tag", "--list", "--sort=-creatordate"], text=True, check=True, capture_output=True)
#    latest_testing_tag = result.stdout.split('\n')[0]
#
#    assert '2026.01.alpha2' == latest_testing_tag

# ---- traceback suppression tests ----
# These tests verify that unhandled exceptions print a clean error message
# at default verbosity, and the full traceback only at -vv.

_CLI_SCRIPT = """\
import sys
sys.argv = {argv!r}
from fre.fre import fre
fre(standalone_mode=True)
"""

def _run_fre_subprocess(argv):
    """Helper: run fre via subprocess so sys.excepthook is exercised."""
    return subprocess.run(
        [sys.executable, "-c", _CLI_SCRIPT.format(argv=argv)],
        capture_output=True, text=True
    )

def test_traceback_suppressed_by_default():
    '''fre run function - default verbosity should suppress traceback'''
    result = _run_fre_subprocess(["fre", "run", "function"])
    assert result.returncode != 0
    assert "NotImplementedError" in result.stderr
    assert "Traceback" not in result.stderr
    assert "fre -vv" in result.stderr

def test_traceback_suppressed_with_single_v():
    '''fre -v run function - single -v should still suppress traceback'''
    result = _run_fre_subprocess(["fre", "-v", "run", "function"])
    assert result.returncode != 0
    assert "NotImplementedError" in result.stderr
    assert "Traceback" not in result.stderr
    assert "fre -vv" in result.stderr

def test_traceback_shown_with_vv():
    '''fre -vv run function - double -v should show full traceback'''
    result = _run_fre_subprocess(["fre", "-vv", "run", "function"])
    assert result.returncode != 0
    assert "NotImplementedError" in result.stderr
    assert "Traceback" in result.stderr
    assert "fre -vv" not in result.stderr
