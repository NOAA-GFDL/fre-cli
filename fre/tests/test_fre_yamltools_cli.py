''' test "fre yamltools" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

def test_cli_fre_yamltools():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_help():
    ''' fre yamltools --help '''
    result = runner.invoke(fre.fre, args=["yamltools", "--help"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_opt_dne():
    ''' fre yamltools optionDNE '''
    result = runner.invoke(fre.fre, args=["yamltools", "optionDNE"])
    assert result.exit_code == 2
