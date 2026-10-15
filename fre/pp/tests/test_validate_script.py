from pathlib import Path
from unittest.mock import call, patch

from fre.pp.validate_script import validate_subtool


def test_validate_subtool_runs_commands_in_workflow_directory(tmp_path, monkeypatch):
    """Validation commands run in the workflow directory without changing caller cwd."""
    monkeypatch.chdir(tmp_path)

    workflow_name = "experiment__platform__target"
    workflow_directory = str(Path.home() / "cylc-src" / workflow_name)

    with (
        patch(
            "fre.pp.validate_script.make_workflow_name",
            return_value=workflow_name,
        ),
        patch("fre.pp.validate_script.subprocess.run") as mock_run,
    ):
        validate_subtool("experiment", "platform", "target")

    assert Path.cwd() == tmp_path

    assert mock_run.call_args_list == [
        call(
            "rose macro --validate",
            shell=True,
            check=True,
            cwd=workflow_directory,
        ),
        call(
            "cylc validate .",
            shell=True,
            check=True,
            cwd=workflow_directory,
        ),
    ]