"""test "fre check" calls"""

from click.testing import CliRunner

from fre import fre

runner = CliRunner()


def test_cli_fre_check():
    """fre check"""
    result = runner.invoke(fre.fre, args=["check"])
    assert result.exit_code == 0


def test_cli_fre_check_help():
    """fre check --help"""
    result = runner.invoke(fre.fre, args=["check", "--help"])
    assert result.exit_code == 0


def test_cli_fre_check_opt_dne():
    """fre check optionDNE"""
    result = runner.invoke(fre.fre, args=["check", "optionDNE"])
    assert result.exit_code == 2
