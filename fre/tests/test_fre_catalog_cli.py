''' test "fre catalog" calls '''

from click.testing import CliRunner

from fre import fre

runner = CliRunner()


def test_cli_fre_catalog():
    ''' fre catalog '''
    result = runner.invoke(fre.fre, args=["catalog"])
    assert result.exit_code == 0


def test_cli_fre_catalog_help():
    ''' fre catalog --help '''
    result = runner.invoke(fre.fre, args=["catalog", "--help"])
    assert result.exit_code == 0


def test_cli_fre_catalog_opt_dne():
    ''' fre catalog optionDNE '''
    result = runner.invoke(fre.fre, args=["catalog", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_catalog_builder():
    ''' fre catalog builder '''
    result = runner.invoke(fre.fre, args=["catalog", "builder"])
    stdout_str = 'Missing: input_path or output_path. ' + \
                 'Pass it in the config yaml or as command-line option'
    assert all([
        result.exit_code == 1,
        stdout_str in result.stdout.split('\n')
    ]
    )


def test_cli_fre_catalog_builder_help():
    ''' fre catalog builder --help '''
    result = runner.invoke(fre.fre, args=["catalog", "builder", "--help"])
    assert result.exit_code == 0


def test_cli_fre_catalog_merge():
    result = runner.invoke(fre.fre, args=["catalog", "merge"])
    expected_stdout = "Error: Missing option '--input'."
    assert all([
        result.exit_code == 2,
        expected_stdout in result.stdout.split('\n')
    ])


def test_cli_fre_catalog_merge_help():
    result = runner.invoke(fre.fre, args=["catalog", "merge", "--help"])
    assert result.exit_code == 0
