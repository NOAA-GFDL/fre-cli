"""Test "fre analysis" tools."""
from click.testing import CliRunner

from fre import fre


runner = CliRunner()


def test_cli_fre_analysis():
    """Most basic invocation of `fre analysis`."""
    result = runner.invoke(fre.fre, args=["analysis"])
    assert result.exit_code == 0


def test_cli_fre_analysis_help():
    """Make sure `fre analysis --help` runs."""
    result = runner.invoke(fre.fre, args=["analysis", "--help"])
    assert result.exit_code == 0


def test_cli_fre_analysis_install_help():
    """Make sure `fre analysis install --help` runs."""
    result = runner.invoke(fre.fre, args=["analysis", "install", "--help"])
    assert result.exit_code == 0


def test_cli_fre_analysis_install_missing_url():
    """Missing the `fre analysis install --url` argument."""
    result = runner.invoke(fre.fre, args=["analysis", "install"])
    assert result.exit_code == 2


def test_cli_fre_analysis_install_unknown_argument():
    """Using an unknown argument with `fre analysis install`."""
    result = runner.invoke(fre.fre, args=["analysis", "install", "bad-arg",])
    assert result.exit_code == 2


def test_cli_fre_analysis_run_help():
    """Make sure `fre analysis run --help` runs."""
    result = runner.invoke(fre.fre, args=["analysis", "run", "--help"])
    assert result.exit_code == 0


def test_cli_fre_analysis_run_missing_name():
    """Missing the `fre analysis run --name` argument."""
    result = runner.invoke(fre.fre, args=["analysis", "run"])
    assert result.exit_code == 2


def test_cli_fre_analysis_run_missing_catalog():
    """Missing the `fre analysis run --catalog` argument."""
    result = runner.invoke(fre.fre, args=["analysis", "run", "--name", "name"])
    assert result.exit_code == 2


def test_cli_fre_analysis_run_missing_output_directory():
    """Missing the `fre analysis run --output-directory` argument."""
    args = ["analysis", "run", "--name", "name", "--catalog", "catalog"]
    result = runner.invoke(fre.fre, args=args)
    assert result.exit_code == 2


def test_cli_fre_analysis_run_missing_output_yaml():
    """Missing the `fre analysis run --output-yaml` argument."""
    args = ["analysis", "run", "--name", "name", "--catalog", "catalog",
            "--output-directory", "dir",]
    result = runner.invoke(fre.fre, args=args)
    assert result.exit_code == 2


def test_cli_fre_analysis_run_missing_experiment_yaml():
    """Missing the `fre analysis run --experiment-yaml` argument."""
    args = ["analysis", "run", "--name", "name", "--catalog", "catalog",
            "--output-directory", "dir", "--output-yaml", "yaml"]
    result = runner.invoke(fre.fre, args=args)
    assert result.exit_code == 2


def test_cli_fre_analysis_run_unknown_argument():
    """Using an unknown argument with `fre analysis run`."""
    result = runner.invoke(fre.fre, args=["analysis", "run", "bad-arg",])
    assert result.exit_code == 2


def test_cli_fre_analysis_uninstall_help():
    """Make sure `fre analysis uninstall --help` runs."""
    result = runner.invoke(fre.fre, args=["analysis", "uninstall", "--help"])
    assert result.exit_code == 0


def test_cli_fre_analysis_uninstall_missing_name():
    """Missing the `fre analysis uninstall --name` argument."""
    result = runner.invoke(fre.fre, args=["analysis", "uninstall"])
    assert result.exit_code == 2


def test_cli_fre_analysis_uninstall_unknown_argument():
    """Using an unknown argument with `fre analysis uninstall`."""
    result = runner.invoke(fre.fre, args=["analysis", "uninstall", "bad-arg",])
    assert result.exit_code == 2
