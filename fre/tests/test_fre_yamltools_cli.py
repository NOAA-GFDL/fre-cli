''' test "fre yamltools" calls '''

from pathlib import Path

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

def test_cli_fre_yamltools_combine_help():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_combine_help():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls", "--help"])
    assert result.exit_code == 0

def test_cli_fre_yamltools_combine_opt_dne():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_yamltools_combine_cmoryaml():
    ''' fre yamltools combine-yamls for cmorization'''
    if Path('FOO_cmor.yaml').exists():
        Path('FOO_cmor.yaml').unlink()
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls",
                                          "-y", "fre/yamltools/tests/AM5_example/am5.yaml",
                                          "-e", "c96L65_am5f7b12r1_amip",
                                          "-p", "ncrc5.intel",
                                          "-t", "prod-openmp",
                                          "--use", "cmor", "--output", "FOO_cmor.yaml"    ])
    assert all ( [ result.exit_code == 0,
                   Path('FOO_cmor.yaml').exists()
    ] )
