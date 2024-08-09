#!/usr/bin/env python3
''' test "fre run" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_run():
    ''' fre run '''
    result = runner.invoke(fre.fre, args=["run"])
    assert result.exit_code == 0

def test_cli_fre_run_help():
    ''' fre run --help '''
    result = runner.invoke(fre.fre, args=["run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_run_opt_dne():
    ''' fre run optionDNE '''
    result = runner.invoke(fre.fre, args=["run", "optionDNE"])
    assert result.exit_code == 2
