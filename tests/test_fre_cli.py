#!/usr/bin/env python3

from fre import fre

from click.testing import CliRunner
runner = CliRunner()


def test_cli_fre():
    result = runner.invoke(fre.fre)
    #print(f'exit code of runner result is {result.exit_code}')
    #print(f'output of runner result is {result.output}')
    assert result.exit_code == 0

def test_cli_fre_help():
    result = runner.invoke(fre.fre,args='--help')
    #print(f'exit code of runner result is {result.exit_code}')
    #print(f'output of runner result is {result.output}')
    assert result.exit_code == 0

def test_cli_fre_option_dne():
    result = runner.invoke(fre.fre,args='optionDNE')
    #print(f'exit code of runner result is {result.exit_code}')
    #print(f'output of runner result is {result.output}')
    assert result.exit_code == 2
