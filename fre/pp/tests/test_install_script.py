"""
Tests for fre pp install: the workflow is validated with 'cylc validate'
before it is installed, and an invalid workflow is not installed.
"""

import subprocess
from unittest import mock

import pytest

from fre.pp import install_script


def _fake_home(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    source_dir = tmp_path / "cylc-src" / "exp__plat__targ"
    source_dir.mkdir(parents=True)
    return source_dir


def test_install_validates_before_install(monkeypatch, tmp_path):
    ''' cylc validate runs in the source dir, then cylc install runs '''
    source_dir = _fake_home(monkeypatch, tmp_path)
    with mock.patch.object(install_script.subprocess, "run") as fake_run:
        install_script.install_subtool("exp", "plat", "targ")

    calls = fake_run.call_args_list
    assert calls[0].args[0] == ["cylc", "validate", "."]
    assert calls[0].kwargs["cwd"] == source_dir
    assert calls[0].kwargs["check"] is True
    assert "cylc install" in calls[-1].args[0]


def test_install_skipped_when_validate_fails(monkeypatch, tmp_path):
    ''' a failing cylc validate raises and cylc install is never called '''
    _fake_home(monkeypatch, tmp_path)

    def fake_run(cmd, *args, **kwargs):
        if cmd == ["cylc", "validate", "."]:
            raise subprocess.CalledProcessError(1, cmd)
        raise AssertionError(f"unexpected command after failed validate: {cmd}")

    with mock.patch.object(install_script.subprocess, "run", side_effect=fake_run):
        with pytest.raises(subprocess.CalledProcessError):
            install_script.install_subtool("exp", "plat", "targ")

    assert not (tmp_path / "cylc-run" / "exp__plat__targ").exists()
