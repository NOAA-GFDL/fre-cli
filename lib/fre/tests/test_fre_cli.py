''' test "fre" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre():
    ''' fre '''
    result = runner.invoke(fre.fre)
    assert result.exit_code == 0

def test_cli_fre_help():
    ''' fre --help '''
    result = runner.invoke(fre.fre, args='--help')
    assert result.exit_code == 0

def test_cli_fre_option_dne():
    ''' fre optionDNE '''
    result = runner.invoke(fre.fre, args='optionDNE')
    assert result.exit_code == 2


def test_fre_version():
    ''' module import flavor of below cli test '''
    assert '2025.04' == fre.version

def test_cli_fre_version():
    ''' fre --version '''
    result = runner.invoke(fre.fre, args='--version')
    expected_out = 'fre, version 2025.04'
    assert all( [ result.exit_code == 0,
                  expected_out in result.stdout.split('\n') ] )
