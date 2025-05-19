""" test "fre app" calls """

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
    assert result.exit_code == 0
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

@pytest.mark.skip(reason="needs rework")
def test_cli_fre_app_regrid_test_case_1(capfd):
    """ fre cmor run --help """

    import fre.app.regrid_xy.tests.test_regrid_xy as t_rgxy
    assert t_rgxy is not None

    # input files for this test are locked up in here as well
    if not Path( t_rgxy.TEST_DIR+'/in-dir' ).exists():
        assert Path(t_rgxy.TAR_IN_DIR).exists()
        ex = [ "tar", "-C", t_rgxy.TEST_DIR, "-zxvf", t_rgxy.TAR_IN_DIR ]
        sp = subprocess.run( ex )
        assert all ( [ sp.returncode == 0,
                       Path(t_rgxy.IN_DIR).exists() ] )

    # for the time being, still a little dependent on rose for configuration value passing
    if Path(os.getcwd()+'/rose-app-run.conf').exists():
        Path(os.getcwd()+'/rose-app-run.conf').unlink()

    with open(os.getcwd()+'/rose-app-run.conf','a',encoding='utf-8') as rose_app_run_config:
        rose_app_run_config.write(  '[command]\n'                    )
        rose_app_run_config.write(  'default=regrid-xy\n'            )
        rose_app_run_config.write(  '\n'                             )
        rose_app_run_config.write( f'[{t_rgxy.COMPONENT}]\n'                )
        rose_app_run_config.write( f'sources={t_rgxy.SOURCE}\n'             )
        rose_app_run_config.write( f'inputGrid={t_rgxy.INPUT_GRID}\n'       )
        rose_app_run_config.write( f'inputRealm={t_rgxy.INPUT_REALM}\n'     )
        rose_app_run_config.write( f'interpMethod={t_rgxy.INTERP_METHOD}\n' )
        rose_app_run_config.write( f'outputGridLon={t_rgxy.NLON}\n'         )
        rose_app_run_config.write( f'outputGridLat={t_rgxy.NLAT}\n'         )
        rose_app_run_config.write(  '\n'                             )
    assert Path('./rose-app-run.conf').exists()

    args_list = ["app", "regrid",
                 "--input_dir", f"{t_rgxy.WORK_YYYYMMDD_DIR}",
                 "--output_dir", f"{t_rgxy.TEST_OUT_DIR}",
                 "--begin", f"{t_rgxy.YYYYMMDD}T000000",
                 "--tmp_dir", f"{t_rgxy.TEST_DIR}",
                 "--remap_dir", f"{t_rgxy.REMAP_DIR}",
                 "--source", f"{t_rgxy.SOURCE}",
                 "--grid_spec", f"{t_rgxy.GOLD_GRID_SPEC_NO_TAR}",
                 "--def_xy_interp", f'"{t_rgxy.NLON},{t_rgxy.NLAT}"' ]
    click.echo(f'args_list = \n {args_list}')
    click.echo('fre ' + ' '.join(args_list))

    result = runner.invoke(fre.fre, args=args_list )
    assert result.exit_code == 0
    _out, _err = capfd.readouterr()
