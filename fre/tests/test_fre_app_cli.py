''' test "fre app" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

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
