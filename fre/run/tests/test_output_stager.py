import tarfile
from contextlib import nullcontext
from pathlib import Path

from click.testing import CliRunner
import click
import pytest

from fre.run import output_stager


def test_validate_path_rejects_missing_path(tmp_path):
    missing_path = tmp_path / "missing"

    with pytest.raises(click.ClickException, match="doesn't exist"):
        output_stager.validate_path(missing_path)


def test_create_tar_archive_contains_work_files(tmp_path):
    work_dir = tmp_path / "work"
    arch_dir = tmp_path / "archive"
    work_dir.mkdir()
    arch_dir.mkdir()
    (work_dir / "input.txt").write_text("staged output")

    output_stager.create_tar_archive(work_dir, arch_dir)

    with tarfile.open(arch_dir / "archive.tar") as archive:
        input_member = next(
            member for member in archive.getmembers()
            if Path(member.name).name == "input.txt"
        )
        assert archive.extractfile(input_member).read() == b"staged output"


def test_output_stager_cli_creates_archive(tmp_path, monkeypatch):
    work_dir = tmp_path / "work"
    arch_dir = tmp_path / "archive"
    work_dir.mkdir()
    arch_dir.mkdir()
    (work_dir / "input.txt").write_text("staged output")
    monkeypatch.setattr(output_stager, "acquire_lock", lambda _: nullcontext())

    result = CliRunner().invoke(
        output_stager.outputStager,
        ["--mode", "history", "experiment", str(work_dir), str(arch_dir)],
    )

    assert result.exit_code == 0, result.output
    assert (arch_dir / "archive.tar").is_file()
