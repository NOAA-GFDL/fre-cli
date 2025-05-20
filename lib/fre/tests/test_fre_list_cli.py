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

## fre list exps
def test_cli_fre_list_exps():
    ''' fre list exps '''
    result = runner.invoke(fre.fre, args=["list", "exps"])
    assert result.exit_code == 2

def test_cli_fre_list_exps_help():
    ''' fre list exps --help '''
    result = runner.invoke(fre.fre, args=["list", "exps", "--help"])
    assert result.exit_code == 0

def test_cli_fre_list_exps_opt_dne():
    ''' fre list exps optionDNE '''
    result = runner.invoke(fre.fre, args=["list", "exps", "optionDNE"])
    assert result.exit_code == 2

## fre list platforms
def test_cli_fre_list_platforms():
    ''' fre list platforms '''
    result = runner.invoke(fre.fre, args=["list", "platforms"])
    assert result.exit_code == 2

def test_cli_fre_list_exps_help():
    ''' fre list platforms --help '''
    result = runner.invoke(fre.fre, args=["list", "platforms", "--help"])
    assert result.exit_code == 0

def test_cli_fre_list_exps_opt_dne():
    ''' fre list platforms optionDNE '''
    result = runner.invoke(fre.fre, args=["list", "platforms", "optionDNE"])
    assert result.exit_code == 2
