"""Output stager helpers and CLI command."""

from __future__ import annotations

import logging
import tarfile
from pathlib import Path

import click


fre_logger = logging.getLogger(__name__)
VALID_MODES = ("history", "ascii", "restart")


def validate_mode(mode: str | None) -> str:
    """Validate output stager mode."""
    if mode is None or mode.lower() not in VALID_MODES:
        valid_modes = ", ".join(VALID_MODES)
        raise ValueError(f"Invalid --mode value. Please choose one of: {valid_modes}.")
    return mode.lower()


def create_archive_tar(arch_dir: Path, work_dir: Path) -> Path:
    """Create a TAR archive from arch_dir contents into work_dir."""
    if not arch_dir.is_dir():
        raise FileNotFoundError(f"Archive directory does not exist: {arch_dir}")
    if not work_dir.is_dir():
        raise FileNotFoundError(f"Work directory does not exist: {work_dir}")

    archive_path = work_dir / "archive.tar"
    with tarfile.open(archive_path, "w") as archive:
        for source in sorted(arch_dir.iterdir()):
            archive.add(source, arcname=source.name)
    return archive_path


@click.command(name="output-stager")
@click.option("--work_dir", required=True, type=click.Path(path_type=Path))
@click.option("--arch_dir", required=True, type=click.Path(path_type=Path))
@click.option("--mode", required=True, type=click.Choice(VALID_MODES, case_sensitive=False))
def outputStager(work_dir: Path, arch_dir: Path, mode: str) -> None:
    """Create a tar archive from arch_dir inside work_dir."""
    try:
        selected_mode = validate_mode(mode)
        fre_logger.info(f"Output stager mode selected: {selected_mode}")
        archive_path = create_archive_tar(arch_dir=arch_dir, work_dir=work_dir)
        fre_logger.info(f"Created archive file: {archive_path}")
    except Exception as exc:
        fre_logger.exception(f"Output stager failed: {exc}")
        raise click.ClickException(str(exc)) from exc
