''' test "fre list" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_list():
    ''' fre list '''
    result = runner.invoke(fre.fre, args=["list"])
    assert result.exit_code == 0

def test_cli_fre_list_help():
    ''' fre list --help '''
    result = runner.invoke(fre.fre, args=["list", "--help"])
    assert result.exit_code == 0

def test_cli_fre_list_opt_dne():
    ''' fre list optionDNE '''
    result = runner.invoke(fre.fre, args=["list", "optionDNE"])
    assert result.exit_code == 2
