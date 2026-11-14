import os
from pathlib import Path

import pytest

from fre.pp.install_script import install_subtool


@pytest.fixture
def workflow(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    workflow_name = "experiment__platform__target"
    source_dir = tmp_path / "cylc-src" / workflow_name
    install_dir = tmp_path / "cylc-run" / workflow_name
    source_dir.mkdir(parents=True)
    install_dir.mkdir(parents=True)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "commands.log"

    executable = bin_dir / "cylc"
    executable.write_text(
        "#!/bin/sh\n"
        'printf "%s|%s\\n" "$(pwd)" "$*" >> "$COMMAND_LOG"\n'
        'if [ "$2" = "." ]; then\n'
        '    cat definition.txt\n'
        'else\n'
        '    cat "$HOME/cylc-run/$2/definition.txt"\n'
        'fi\n'
    )
    executable.chmod(0o755)

    monkeypatch.setenv("COMMAND_LOG", str(log_file))
    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)

    return workflow_name, source_dir, install_dir, log_file


def test_install_subtool_reads_source_config_without_changing_cwd(
    tmp_path,
    workflow,
):
    """Source config is read from source_dir without changing caller cwd."""
    workflow_name, source_dir, install_dir, log_file = workflow

    (source_dir / "definition.txt").write_text("same config")
    (install_dir / "definition.txt").write_text("same config")

    install_subtool("experiment", "platform", "target")

    assert Path.cwd() == tmp_path
    assert log_file.read_text().splitlines() == [
        f"{tmp_path}|config {workflow_name}",
        f"{source_dir}|config .",
    ]


def test_install_changed_definition_does_not_change_cwd(
    tmp_path,
    workflow,
):
    """Caller cwd is unchanged when the definition has changed."""
    workflow_name, source_dir, install_dir, log_file = workflow

    (source_dir / "definition.txt").write_text("changed source config")
    (install_dir / "definition.txt").write_text("installed config")

    with pytest.raises(Exception, match="definition has changed"):
        install_subtool("experiment", "platform", "target")

    assert Path.cwd() == tmp_path
    assert log_file.read_text().splitlines() == [
        f"{tmp_path}|config {workflow_name}",
        f"{source_dir}|config .",
    ]
