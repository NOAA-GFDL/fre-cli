"""Test fre dora cli."""
from click.testing import CliRunner

from fre import fre


runner = CliRunner()


def test_cli_fre_dora():
    """Most basic invocation of fre dora."""
    result = runner.invoke(fre.fre, args=["dora"])
    assert result.exit_code == 0


def test_cli_fre_dora_help():
    """Make sure fre dora --help runs."""
    result = runner.invoke(fre.fre, args=["dora", "--help"])
    assert result.exit_code == 0


def test_cli_fre_dora_add_help():
    """Make sure fre dora add --help runs."""
    result = runner.invoke(fre.fre, args=["dora", "add", "--help"])
    assert result.exit_code == 0


def test_cli_fre_dora_add_missing_experiment_yaml():
    """Missing the fre dora add --experiment-yaml argument."""
    result = runner.invoke(fre.fre, args=["dora", "add"])
    assert result.exit_code == 2


def test_cli_fre_dora_add_unknown_argument():
    """Using an unknown argument with fre dora add."""
    result = runner.invoke(fre.fre, args=["dora", "add", "bad-arg",])
    assert result.exit_code == 2


def test_cli_fre_dora_get_help():
    """Make sure fre dora get --help runs."""
    result = runner.invoke(fre.fre, args=["dora", "get", "--help"])
    assert result.exit_code == 0


def test_cli_fre_dora_get_missing_experiment_yaml():
    """Missing the fre dora get --experiment-yaml argument."""
    result = runner.invoke(fre.fre, args=["dora", "get"])
    assert result.exit_code == 2


def test_cli_fre_dora_get_unknown_argument():
    """Using an unknown argument with fre dora get."""
    result = runner.invoke(fre.fre, args=["dora", "get", "bad-arg"])
    assert result.exit_code == 2


def test_cli_fre_dora_publish_help():
    """Make sure fre dora publish --help runs."""
    result = runner.invoke(fre.fre, args=["dora", "publish", "--help"])
    assert result.exit_code == 0


def test_cli_fre_dora_publish_missing_name():
    """Missing the fre dora publish --name argument."""
    result = runner.invoke(fre.fre, args=["dora", "publish"])
    assert result.exit_code == 2


def test_cli_fre_dora_publish_missing_experiment_yaml():
    """Missing the fre dora publish --experiment-yaml argument."""
    args = ["dora", "publish", "--name", "name"]
    result = runner.invoke(fre.fre, args=args)
    assert result.exit_code == 2


def test_cli_fre_dora_publish_missing_figures_yaml():
    """Missing the fre dora publish --figures-yaml argument."""
    args = ["dora", "publish", "--name", "name", "--experiment-yaml", "experiment"]
    result = runner.invoke(fre.fre, args=args)
    assert result.exit_code == 2


def test_cli_fre_dora_publish_unknown_argument():
    """Using an unknown argument with fre dora publish."""
    result = runner.invoke(fre.fre, args=["dora", "publish", "bad-arg",])
    assert result.exit_code == 2
