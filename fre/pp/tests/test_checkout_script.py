from pathlib import Path
from unittest.mock import Mock, call, patch

from fre.pp.checkout_script import (
    FRE_WORKFLOWS_URL,
    checkout_template,
)


def test_checkout_existing_workflow_runs_git_commands_in_workflow_directory(
    tmp_path,
    monkeypatch,
):
    """Git inspection commands run in the checkout without changing caller cwd."""
    monkeypatch.chdir(tmp_path)

    workflow_name = "experiment__platform__target"
    branch = "test-branch"
    workflow_directory = str(Path.home() / "cylc-src" / workflow_name)

    with (
        patch(
            "fre.pp.checkout_script.make_workflow_name",
            return_value=workflow_name,
        ),
        patch("fre.pp.checkout_script.os.makedirs"),
        patch(
            "fre.pp.checkout_script.os.path.isdir",
            return_value=True,
        ),
        patch(
            "fre.pp.checkout_script.subprocess.run",
            side_effect=[
                Mock(stdout="different-tag\n"),
                Mock(stdout=f"{branch}\n"),
            ],
        ) as mock_run,
    ):
        checkout_template(
            "experiment",
            "platform",
            "target",
            branch=branch,
        )

    assert Path.cwd() == tmp_path

    assert mock_run.call_args_list == [
        call(
            ["git", "describe", "--tags"],
            cwd=workflow_directory,
            capture_output=True,
            text=True,
            check=True,
        ),
        call(
            ["git", "branch", "--show-current"],
            cwd=workflow_directory,
            capture_output=True,
            text=True,
            check=True,
        ),
    ]


def test_checkout_missing_workflow_clones_into_workflow_directory(
    tmp_path,
    monkeypatch,
):
    """A missing workflow is cloned directly into its expected directory."""
    monkeypatch.chdir(tmp_path)

    workflow_name = "experiment__platform__target"
    branch = "test-branch"
    workflow_directory = str(Path.home() / "cylc-src" / workflow_name)

    with (
        patch(
            "fre.pp.checkout_script.make_workflow_name",
            return_value=workflow_name,
        ),
        patch("fre.pp.checkout_script.os.makedirs"),
        patch(
            "fre.pp.checkout_script.os.path.isdir",
            return_value=False,
        ),
        patch(
            "fre.pp.checkout_script.subprocess.run",
            return_value=Mock(),
        ) as mock_run,
    ):
        checkout_template(
            "experiment",
            "platform",
            "target",
            branch=branch,
        )

    assert Path.cwd() == tmp_path

    mock_run.assert_called_once_with(
        [
            "git",
            "clone",
            "--recursive",
            f"--branch={branch}",
            FRE_WORKFLOWS_URL,
            workflow_directory,
        ],
        capture_output=True,
        text=True,
        check=True,
    )