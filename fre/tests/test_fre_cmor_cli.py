"""
CLI Tests to make sure fre cmor * exit the right way
"""

from click.testing import CliRunner

from fre import fre

runner = CliRunner()

# fre cmor
def test_cli_fre_cmor():
    ''' fre cmor '''
    result = runner.invoke(fre.fre, args=["cmor"])
    assert result.exit_code == 2

def test_cli_fre_cmor_help():
    ''' fre cmor --help '''
    result = runner.invoke(fre.fre, args=["cmor", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_opt_dne():
    ''' fre cmor optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "optionDNE"])
    assert result.exit_code == 2

# fre cmor yaml
def test_cli_fre_cmor_yaml():
    ''' fre cmor yaml '''
    result = runner.invoke(fre.fre, args=["cmor", "yaml"])
    assert result.exit_code == 1

def test_cli_fre_cmor_yaml_help():
    ''' fre cmor yaml --help '''
    result = runner.invoke(fre.fre, args=["cmor", "yaml", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_yaml_opt_dne():
    ''' fre cmor yaml optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "yaml", "optionDNE"])
    assert result.exit_code == 2

# fre cmor run
def test_cli_fre_cmor_run():
    ''' fre cmor run '''
    result = runner.invoke(fre.fre, args=["cmor", "run"])
    assert result.exit_code == 1

def test_cli_fre_cmor_run_help():
    ''' fre cmor run --help '''
    result = runner.invoke(fre.fre, args=["cmor", "run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_run_opt_dne():
    ''' fre cmor run optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "run", "optionDNE"])
    assert result.exit_code == 2

# fre cmor find
def test_cli_fre_cmor_find():
    ''' fre cmor find '''
    result = runner.invoke(fre.fre, args=["cmor", "find"])
    assert result.exit_code == 1

def test_cli_fre_cmor_find_help():
    ''' fre cmor find --help '''
    result = runner.invoke(fre.fre, args=["cmor", "find", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_find_opt_dne():
    ''' fre cmor find optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "find", "optionDNE"])
    assert result.exit_code == 2

# fre cmor config
def test_cli_fre_cmor_config():
    ''' fre cmor config '''
    result = runner.invoke(fre.fre, args=["cmor", "config"])
    assert result.exit_code == 1

def test_cli_fre_cmor_config_help():
    ''' fre cmor config --help '''
    result = runner.invoke(fre.fre, args=["cmor", "config", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_config_opt_dne():
    ''' fre cmor config optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "config", "optionDNE"])
    assert result.exit_code == 2

# fre cmor varlist
def test_cli_fre_cmor_varlist():
    ''' fre cmor varlist '''
    result = runner.invoke(fre.fre, args=["cmor", "varlist"])
    assert result.exit_code == 1

def test_cli_fre_cmor_varlist_help():
    ''' fre cmor varlist --help '''
    result = runner.invoke(fre.fre, args=["cmor", "varlist", "--help"])
    assert result.exit_code == 0

def test_cli_fre_cmor_varlist_opt_dne():
    ''' fre cmor varlist optionDNE '''
    result = runner.invoke(fre.fre, args=["cmor", "varlist", "optionDNE"])
    assert result.exit_code == 2
