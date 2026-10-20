"""
Test the default branch/tag selection of checkout_script, without cloning
"""
import subprocess

import pytest

from fre.pp import checkout_script

@pytest.mark.parametrize("fre_ver, expected_branch",
                         [ ("2026.01", "2026.01"),
                           ("2026.02.alpha2", "2026.02.alpha2"),
                           ("2026.01-dev", "main"),
                           ("2026.02.alpha2-dev", "main") ])
def test_checkout_default_branch(tmp_path, monkeypatch, fre_ver, expected_branch):
    """
    Release and pre-release versions of fre check out the matching tag,
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
    monkeypatch.setattr(checkout_script, "fre_ver", "2026.01-dev")

    calls = []
    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0)
    monkeypatch.setattr(checkout_script.subprocess, "run", fake_run)

    checkout_script.checkout_template(experiment = "FOO", platform = "BAR", target = "BAZ",
                                      branch = "2026.01")

    assert '--branch=2026.01' in calls[0]
