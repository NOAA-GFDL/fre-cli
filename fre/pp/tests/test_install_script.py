from pathlib import Path
from unittest.mock import Mock, call, patch

from fre.pp.install_script import install_subtool


def test_install_subtool_reads_source_config_without_changing_cwd(
    tmp_path,
    monkeypatch,
):
    """Source config is read from source_dir without changing caller cwd."""
    monkeypatch.chdir(tmp_path)

    workflow_name = "experiment__platform__target"
    source_dir = Path.home() / "cylc-src" / workflow_name

    with (
        patch(
            "fre.pp.install_script.make_workflow_name",
            return_value=workflow_name,
        ),
        patch(
            "fre.pp.install_script.os.path.isdir",
            return_value=True,
        ),
        patch(
            "fre.pp.install_script.subprocess.run",
            side_effect=[
                Mock(stdout=b"same config"),
                Mock(stdout=b"same config"),
            ],
        ) as mock_run,
    ):
        install_subtool("experiment", "platform", "target")

    assert Path.cwd() == tmp_path

    assert mock_run.call_args_list == [
        call(
            ["cylc", "config", workflow_name],
            capture_output=True,
        ),
        call(
            ["cylc", "config", "."],
            cwd=source_dir,
            capture_output=True,
        ),
    ]