''' test "fre app" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

# fre app
def test_cli_fre_app():
    ''' fre app '''
    result = runner.invoke(fre.fre, args=["app"])
    assert result.exit_code == 0

def test_cli_fre_app_help():
    ''' fre app --help '''
    result = runner.invoke(fre.fre, args=["app", "--help"])
    assert result.exit_code == 0

def test_cli_fre_app_opt_dne():
    ''' fre app optionDNE '''
    result = runner.invoke(fre.fre, args=["app", "optionDNE"])
    assert result.exit_code == 2

# fre app gen-time-averages
def test_cli_fre_app_gen_time_averages():
    ''' fre cmor run '''
    result = runner.invoke(fre.fre, args=["app", "gen-time-averages"])
    assert result.exit_code == 2

def test_cli_fre_app_gen_time_averages_help():
    ''' fre cmor run --help '''
    result = runner.invoke(fre.fre, args=["app", "gen-time-averages", "--help"])
    assert result.exit_code == 0

def test_cli_fre_app_gen_time_averages_opt_dne():
    ''' fre cmor run optionDNE '''
    result = runner.invoke(fre.fre, args=["app", "gen-time-averages", "optionDNE"])
    assert result.exit_code == 2

# fre app regrid
def test_cli_fre_app_regrid():
    ''' fre cmor run '''
    result = runner.invoke(fre.fre, args=["app", "regrid"])
    assert result.exit_code == 2

def test_cli_fre_app_regrid_help():
    ''' fre cmor run --help '''
    result = runner.invoke(fre.fre, args=["app", "regrid", "--help"])
    assert result.exit_code == 0

def test_cli_fre_app_regrid_opt_dne():
    ''' fre cmor run optionDNE '''
    result = runner.invoke(fre.fre, args=["app", "regrid", "optionDNE"])
    assert result.exit_code == 2
    
