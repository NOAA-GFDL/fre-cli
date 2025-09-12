""" test "fre app" calls """
"""
CLI Tests for fre app *
Tests the command-line-interface calls for tools in the fre apps. 
Each tool generally gets 3 tests:
    - fre app $tool, checking for exit code 0 (fails if cli isn't configured right)
    - fre app $tool --help, checking for exit code 0 (fails if the code doesn't run)
    - fre app $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured 
      right and thinks the tool has a --optionDNE option)
"""

import os
import subprocess
from pathlib import Path
import pytest

import click
from click.testing import CliRunner

from fre import fre

runner = CliRunner()

# fre app
def test_cli_fre_app(capfd):
    """ fre app """
    result = runner.invoke(fre.fre, args=["app"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

def test_cli_fre_app_help(capfd):
    """ fre app --help """
    result = runner.invoke(fre.fre, args=["app", "--help"])
    assert result.exit_code == 0
    _out, _err = capfd.readouterr()

def test_cli_fre_app_opt_dne(capfd):
    """ fre app optionDNE """
    result = runner.invoke(fre.fre, args=["app", "optionDNE"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

# fre app gen-time-averages
def test_cli_fre_app_gen_time_averages(capfd):
    """ fre cmor run """
    result = runner.invoke(fre.fre, args=["app", "gen-time-averages"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

def test_cli_fre_app_gen_time_averages_help(capfd):
    """ fre cmor run --help """
    result = runner.invoke(fre.fre, args=["app", "gen-time-averages", "--help"])
    assert result.exit_code == 0
    _out, _err = capfd.readouterr()

def test_cli_fre_app_gen_time_averages_opt_dne(capfd):
    """ fre cmor run optionDNE """
    result = runner.invoke(fre.fre, args=["app", "gen-time-averages", "optionDNE"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

# fre app regrid
def test_cli_fre_app_regrid(capfd):
    """ fre cmor run """
    result = runner.invoke(fre.fre, args=["app", "regrid"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

def test_cli_fre_app_regrid_help(capfd):
    """ fre cmor run --help """
    result = runner.invoke(fre.fre, args=["app", "regrid", "--help"])
    assert result.exit_code == 0
    _out, _err = capfd.readouterr()

def test_cli_fre_app_regrid_opt_dne(capfd):
    """ fre cmor run optionDNE """
    result = runner.invoke(fre.fre, args=["app", "regrid", "optionDNE"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

#@pytest.mark.skip(reason="needs rework")
def test_cli_fre_app_regrid_test_case_1(capfd):
    """ fre cmor run --help """

    import fre.app.regrid_xy.tests.test_regrid_xy as test_regrid_xy
    test_regrid_xy.setup_test()        
    
    args_list = ["app", "regrid",
                 "--yamlfile", str(test_regrid_xy.yamlfile),
                 "--input_dir", str(test_regrid_xy.input_dir),
                 "--output_dir", str(test_regrid_xy.output_dir),
                 "--work_dir", str(test_regrid_xy.work_dir),
                 "--remap_dir", str(test_regrid_xy.remap_dir),
                 "--source", "pemberley",
                 "--input_date", test_regrid_xy.date+"T000000"]
    click.echo(f"args_list = \n {args_list}")
    click.echo("fre " + ' '.join(args_list))

    result = runner.invoke(fre.fre, args=args_list )
    assert result.exit_code == 0
    _out, _err = capfd.readouterr()

# fre app remap
def test_cli_fre_app_remap(capfd):
    """ fre app remap """
    result = runner.invoke(fre.fre, args=["app", "remap"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

def test_cli_fre_app_remap_help(capfd):
    """ fre app remap --help """
    result = runner.invoke(fre.fre, args=["app", "remap", "--help"])
    assert result.exit_code == 0
    _out, _err = capfd.readouterr()

def test_cli_fre_app_remap_opt_dne(capfd):
    """ fre app remap optionDNE """
    result = runner.invoke(fre.fre, args=["app", "remap", "optionDNE"])
    assert result.exit_code == 2
    _out, _err = capfd.readouterr()

