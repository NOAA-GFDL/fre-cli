''' test "fre test" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_test():
    ''' fre test '''
    result = runner.invoke(fre.fre, args=["test"])
    assert result.exit_code == 0

def test_cli_fre_test_help():
    ''' fre test --help '''
    result = runner.invoke(fre.fre, args=["test", "--help"])
    assert result.exit_code == 0

def test_cli_fre_test_opt_dne():
    ''' fre test optionDNE '''
    result = runner.invoke(fre.fre, args=["test", "optionDNE"])
    assert result.exit_code == 2
