"""
Tests for workflow checkout, branch selection, and CWD preservation.
"""
import subprocess
from pathlib import Path

import pytest

from fre.pp import checkout_script
from fre.pp.checkout_script import checkout_template


@pytest.fixture
def local_workflow_repo(tmp_path, monkeypatch):
    """Create a temporary Git repository for checkout tests."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    repo = tmp_path / "source-workflow"
    repo.mkdir()

    def git(*args):
        subprocess.run(
            ["git", *args],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )

    git("init")
    git("checkout", "-b", "test-branch")

    (repo / "README.md").write_text("test workflow\n")
    git("add", "README.md")
    git(
        "-c", "user.name=Test",
        "-c", "user.email=test@example.invalid",
        "commit", "-m", "Initial commit",
    )
    git("tag", "test-tag")

    monkeypatch.setattr(checkout_script, "FRE_WORKFLOWS_URL", str(repo))

    return repo



def test_checkout_existing_workflow_runs_git_commands_in_workflow_directory(
    tmp_path,
    local_workflow_repo,
):
    """Existing workflow is verified without changing caller cwd."""
    branch = "test-branch"
    workflow_directory = tmp_path / "cylc-src" / "experiment__platform__target"

    assert Path.home() == tmp_path
    assert checkout_script.FRE_WORKFLOWS_URL == str(local_workflow_repo)

    checkout_template("experiment", "platform", "target", branch=branch)
    assert (workflow_directory / ".git").is_dir()

    checkout_template("experiment", "platform", "target", branch=branch)

    assert Path.cwd() == tmp_path

    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=workflow_directory,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert current_branch == branch


def test_checkout_missing_workflow_clones_into_workflow_directory(
    tmp_path,
    local_workflow_repo,
):
    """A missing workflow is cloned directly into its expected directory."""
    branch = "test-branch"
    workflow_directory = tmp_path / "cylc-src" / "experiment__platform__target"

    assert Path.home() == tmp_path
    assert checkout_script.FRE_WORKFLOWS_URL == str(local_workflow_repo)
    assert workflow_directory.parent == tmp_path / "cylc-src"
    assert not workflow_directory.exists()

    checkout_template(
        "experiment",
        "platform",
        "target",
        branch=branch,
    )

    assert Path.cwd() == tmp_path
    assert (workflow_directory / ".git").is_dir()
    assert (workflow_directory / "README.md").read_text() == "test workflow\n"

    current_branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=workflow_directory,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    assert current_branch == branch



def test_checkout_branch_mismatch_does_not_change_cwd(
    tmp_path,
    local_workflow_repo,
):
    """Caller cwd is unchanged when the checkout branch/tag does not match the requested branch/tag."""
    workflow_directory = tmp_path / "cylc-src" / "experiment__platform__target"

    assert Path.home() == tmp_path
    assert checkout_script.FRE_WORKFLOWS_URL == str(local_workflow_repo)

    checkout_template("experiment", "platform", "target", branch="test-branch")

    assert (workflow_directory / ".git").is_dir()
    assert Path.cwd() == tmp_path

    with pytest.raises(ValueError, match="neither tag nor branch matches"):
        checkout_template("experiment", "platform", "target", branch="different-branch")

    assert Path.cwd() == tmp_path
    assert (workflow_directory / ".git").is_dir()


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
