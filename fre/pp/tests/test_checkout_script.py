"""
Tests for workflow checkout, branch selection, and CWD preservation.
"""
import subprocess
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from fre.pp import checkout_script
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


def test_checkout_branch_mismatch_does_not_change_cwd(
    tmp_path,
    monkeypatch,
):
    """Caller cwd is unchanged when the checkout branch/tag does not match the requested branch/tag."""
    monkeypatch.chdir(tmp_path)

    workflow_name = "experiment__platform__target"
    branch = "test-branch"

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
                Mock(stdout="different-branch\n"),
            ],
        ),
        pytest.raises(
            ValueError,
            match="neither tag nor branch matches",
        ),
    ):
        checkout_template(
            "experiment",
            "platform",
            "target",
            branch=branch,
        )

    assert Path.cwd() == tmp_path


@pytest.mark.parametrize("fre_ver, expected_branch",
                         [ ("2026.01", "2026.01"),
                           ("2026.02.alpha2", "2026.02.alpha2"),
                           ("develop", "main") ])
def test_checkout_default_branch(tmp_path, monkeypatch, fre_ver, expected_branch):
    """
    Release and pre-release versions of fre check out the matching tag (i.e. fre --version),
    development versions check out the main branch
    """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(checkout_script, "fre_ver", fre_ver)

    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr(checkout_script.subprocess, "run", fake_run)

    checkout_script.checkout_template(experiment = "FOO", platform = "BAR", target = "BAZ")

    assert calls[0][:2] == ['git', 'clone']
    assert f'--branch={expected_branch}' in calls[0]

def test_checkout_explicit_branch(tmp_path, monkeypatch):
    """ a user-specified branch overrides the default, even for development versions """
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(checkout_script, "fre_ver", "develop")

    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr(checkout_script.subprocess, "run", fake_run)

    checkout_script.checkout_template(experiment = "FOO", platform = "BAR", target = "BAZ",
                                      branch = "2026.01")

    assert '--branch=2026.01' in calls[0]
