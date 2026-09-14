"""
CLI Tests for fre run *

Tests the command-line-interface calls for tools in the fre run suite. 
Each tool generally gets 3 tests:

- fre run $tool, checking for exit code 0 (fails if cli isn't configured right)
- fre run $tool --help, checking for exit code 0 (fails if the code doesn't run)
- fre run $tool --optionDNE, checking for exit code 2 (fails if cli isn't configured 
  right and thinks the tool has a --optionDNE option)
"""

from click.testing import CliRunner
import tarfile

from fre import fre

runner = CliRunner()

def test_cli_fre_run():
    ''' fre run '''
    result = runner.invoke(fre.fre, args=["run"])
    assert result.exit_code == 2

def test_cli_fre_run_help():
    ''' fre run --help '''
    result = runner.invoke(fre.fre, args=["run", "--help"])
    assert result.exit_code == 0

def test_cli_fre_run_opt_dne():
    ''' fre run optionDNE '''
    result = runner.invoke(fre.fre, args=["run", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_run_output_stager_invalid_mode():
    """fre run output-stager --mode invalid"""
    with runner.isolated_filesystem():
        result = runner.invoke(
            fre.fre,
            args=["run", "output-stager", "--work_dir", ".", "--arch_dir", ".", "--mode", "bad"],
        )
        assert result.exit_code == 2
        assert "Invalid value for '--mode'" in result.output
        assert "history" in result.output
        assert "ascii" in result.output
        assert "restart" in result.output


def test_cli_fre_run_output_stager_mode_required():
    """fre run output-stager requires --mode"""
    with runner.isolated_filesystem():
        result = runner.invoke(
            fre.fre,
            args=["run", "output-stager", "--work_dir", ".", "--arch_dir", "."],
        )
        assert result.exit_code == 2
        assert "Missing option '--mode'" in result.output
        assert "history" in result.output
        assert "ascii" in result.output
        assert "restart" in result.output


def test_cli_fre_run_output_stager_creates_tar():
    """fre run output-stager creates archive.tar in work dir."""
    with runner.isolated_filesystem():
        with open("source_file.txt", "w", encoding="utf-8") as source_file:
            source_file.write("test-data")

        result = runner.invoke(
            fre.fre,
            args=["run", "output-stager", "--work_dir", ".", "--arch_dir", ".", "--mode", "history"],
        )

        assert result.exit_code == 0
        assert "archive.tar" in result.output or result.output == ""
        assert tarfile.is_tarfile("archive.tar")

        with tarfile.open("archive.tar", "r") as archive:
            assert "source_file.txt" in archive.getnames()
