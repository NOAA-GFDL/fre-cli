import os
from pathlib import Path

from fre.pp.validate_script import validate_subtool


def test_validate_subtool_runs_commands_in_workflow_directory(tmp_path, monkeypatch):
    """Validation commands run in the workflow directory without changing caller cwd."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))

    workflow_name = "experiment__platform__target"
    workflow_directory = tmp_path / "cylc-src" / workflow_name
    workflow_directory.mkdir(parents=True)

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "commands.log"

    for command in ("rose", "cylc"):
        executable = bin_dir / command
        executable.write_text(
            "#!/bin/sh\n"
            f'printf "%s|%s\\n" "$(pwd)" "$*" >> "{log_file}"\n'
        )
        executable.chmod(0o755)

    monkeypatch.setenv("PATH", str(bin_dir), prepend=os.pathsep)

    validate_subtool("experiment", "platform", "target")

    assert Path.cwd() == tmp_path
    assert log_file.read_text().splitlines() == [
        f"{workflow_directory}|macro --validate",
        f"{workflow_directory}|validate .",
    ]
