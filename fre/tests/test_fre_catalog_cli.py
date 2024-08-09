#!/usr/bin/env python3

# tests are structured in the manner of:
# https://click.palletsprojects.com/en/8.1.x/testing/
# general intent is to test the cli of each (sub)tool
# command, help, command does not exist

from click.testing import CliRunner
runner = CliRunner()

from fre import fre

# tests for base 'fre catalog' calls

def test_cli_fre_catalog():
    result = runner.invoke(fre.fre, args=["catalog"])
    assert result.exit_code == 0

def test_cli_fre_catalog_help():
    result = runner.invoke(fre.fre, args=["catalog", "--help"])
    assert result.exit_code == 0

def test_cli_fre_catalog_opt_dne():
    result = runner.invoke(fre.fre, args=["catalog", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_catalog_builder():
    result = runner.invoke(fre.fre, args=["catalog", "builder", "--help"])
    assert result.exit_code == 0

def test_cli_fre_catalog_builder():
    result = runner.invoke(fre.fre, args=["catalog", "builder"])
    assert all( [
                  result.exit_code == 1,
                  'No paths given, using yaml configuration'
                    in result.stdout.split('\n')
                ]
              )
