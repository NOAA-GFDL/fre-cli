"""fre run output stager."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import logging
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from typing import Optional

import click

fre_logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RunContext:
    """Immutable runtime context for the output stager."""

    job_name: Optional[str] = None
    stdout_dir: Optional[str] = None
    is_batch: bool = False


def requeue_slurm_job() -> None:
    """Requeue the active Slurm job if running under Slurm."""
    job_id = os.getenv("SLURM_JOB_ID")
    if not job_id:
        return

    fre_logger.warning("Requeuing Slurm job ID: %s", job_id)
    try:
        subprocess.run(
            ["scontrol", "requeue", job_id],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        fre_logger.error("Failed to requeue Slurm job %s: %s", job_id, exc)


def setup_run_context(verbose: bool = False) -> RunContext:
    """Initialize logging banners and detect the execution environment."""
    if verbose:
        fre_logger.setLevel(logging.DEBUG)

    host = os.getenv("HOST") or socket.gethostname()
    current_date = datetime.now().strftime("%a %b %d %H:%M:%S %Y")

    fre_logger.info("<NOTE> : ====== FRE OUTPUT STAGER ======")
    fre_logger.info("<NOTE> : Starting at %s on %s", host, current_date)

    slurm_job_id = os.getenv("SLURM_JOB_ID")
    slurm_job_name = os.getenv("SLURM_JOB_NAME", "")
    slurm_submit_dir = os.getenv("SLURM_SUBMIT_DIR")
    is_non_interactive = not sys.stdin.isatty()

    if slurm_job_id and is_non_interactive:
        base_name = Path(slurm_job_name).name if slurm_job_name else "fre"
        job_name = f"{base_name}.o{slurm_job_id}"
        return RunContext(
            job_name=job_name,
            stdout_dir=slurm_submit_dir,
            is_batch=True,
        )

    return RunContext()


def validate_path(path_value: str | Path, *, must_be_file: bool = False) -> Path:
    """Validate that a path exists and is accessible."""
    path = Path(path_value)

    if not path.exists():
        fre_logger.error("*ERROR*: The pathname '%s' doesn't exist", path)
        raise click.ClickException(f"The pathname '{path}' doesn't exist")

    if must_be_file and not path.is_file():
        fre_logger.error("*ERROR*: The pathname '%s' exists, but it's not a file", path)
        raise click.ClickException(f"The pathname '{path}' exists, but it's not a file")

    if not os.access(path, os.R_OK):
        fre_logger.error("*ERROR*: The pathname '%s' must be readable", path)
        raise click.ClickException(f"The pathname '{path}' must be readable")

    return path


@contextmanager
def acquire_lock(lock_target: Path):
    """Acquire and release a file lock using the system lockfile utility if available."""
    lock_binary = shutil.which("lockfile")
    lock_file = Path(f"{lock_target}.lock")

    if not lock_binary:
        fre_logger.warning(
            "WARNING: File locking utility 'lockfile' is missing on this host"
        )
        yield
        return

    cmd = [lock_binary, "-60", "-r", "10", "-l", "58200", str(lock_file)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        fre_logger.error(
            "*ERROR*: The target '%s' is locked by another process",
            lock_target,
        )
        raise click.ClickException(
            f"The target '{lock_target}' is locked by another process"
        ) from exc

    try:
        yield
    finally:
        lock_file.unlink(missing_ok=True)

@click.command()
@click.option("--exit-status", is_flag=True, default=False, required=False,
    help="Set to indicate a non-zero exit status from the model run.")
@click.option("--combine", is_flag=True, default=False, required=False,
    help="Enable the combine step for history output files.")
@click.option("--check", is_flag=True, default=False, required=False,
    help="Enable the check step to verify output files.")
@click.option("--save-on", is_flag=True, default=False, required=False,
    help="Enable saving of history output files.")
@click.option("--fill-grid-on", is_flag=True, default=False, required=False,
    help="Enable the fill-grid step.")
@click.option("--combine-ok", is_flag=True, default=False, required=False,
    help="Indicate that the combine step completed successfully.")
@click.option("--check-ok", is_flag=True, default=False, required=False,
    help="Indicate that the check step completed successfully.")
@click.option("--save-ok", is_flag=True, default=False, required=False,
    help="Indicate that the save step completed successfully.")
@click.option("--fill-grid-ok", is_flag=True, default=False, required=False,
    help="Indicate that the fill-grid step completed successfully.")
@click.option("--archive-on", is_flag=True, default=False, required=False,
    help="Enable archiving of history output files.")
@click.option("--ptmp-on", is_flag=True, default=False, required=False,
    help="Enable staging of output files to the ptmp directory.")
@click.option("--check-sum-on", is_flag=True, default=False, required=False,
    help="Enable checksum verification of output files.")
@click.option("--compress-on", is_flag=True, default=False, required=False,
    help="Enable compression of output files.")
@click.option("--verbose", is_flag=True, default=False, required=False,
    help="Enable verbose output.")
@click.argument("exp_name")
@click.argument("output_type")
@click.argument("work_dir")
@click.argument("ptmp_dir")
@click.argument("arch_dir")
@click.argument("mppnccombine_opt_string")
@click.argument("ardiff_tmpdir")
def outputStager(exit_status, combine, check, save_on, fill_grid_on,  # pylint: disable=invalid-name
                 combine_ok, check_ok, save_ok, fill_grid_ok, archive_on,
                 ptmp_on, check_sum_on, compress_on, verbose,
                 exp_name, output_type, work_dir, ptmp_dir, arch_dir,
                 mppnccombine_opt_string, ardiff_tmpdir):
    """Stage output files for post-processing."""
    setup_run_context(verbose=verbose)

    work_dir_path = validate_path(work_dir)
    ptmp_dir_path = validate_path(ptmp_dir)
    arch_dir_path = validate_path(arch_dir)
    ardiff_tmpdir_path = validate_path(ardiff_tmpdir)

    lock_target = work_dir_path / f"{exp_name}.{output_type}"
    try:
        with acquire_lock(lock_target):
            pass  # USE ABOVE FUNCTIONS
    except KeyboardInterrupt:
        # Lock is released by acquire_lock's finally clause ("unlock"),
        # then requeue if under Slurm (mirrors tcsh CATCH_SIGINT).
        fre_logger.warning("Interrupt received; requeuing if under Slurm.")
        requeue_slurm_job()
        sys.exit(130)
