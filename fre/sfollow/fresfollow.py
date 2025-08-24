"""
FRE SFollow CLI - Click command line interface for following SLURM job output

This module provides the Click CLI interface for the sfollow functionality.

authored by Tom Robinson
NOAA | GFDL
2025
"""

import sys
import click
from .sfollow import follow_job_output


@click.command(help=click.style(" - follow SLURM job output in real-time", fg=(34, 139, 34)))
@click.argument('job_id', type=str, required=True)
@click.option('--validate', '-v', is_flag=True,
              help='Validate job exists and has output file without following')
def sfollow_cli(job_id, validate):
    """
    Follow the standard output of a SLURM job in real-time.

    This command queries the SLURM scheduler for job information,
    extracts the standard output file path, and follows it using
    'less +F' for real-time monitoring.

    :param job_id: The SLURM job ID to follow
    :type job_id: str
    :param validate: If True, only validate the job without following
    :type validate: bool

    Examples:
        fre sfollow 12345
        fre sfollow 12345 --validate
    """
    if validate:
        click.echo(f"Validating job {job_id}...")
        # For validation, we'll just try to get the job info and stdout path
        try:
            from .sfollow import get_job_info, parse_stdout_path
            job_info = get_job_info(job_id)
            stdout_path = parse_stdout_path(job_info)

            if stdout_path:
                click.echo(f"✓ Job {job_id} found")
                click.echo(f"✓ Standard output file: {stdout_path}")
                sys.exit(0)
            else:
                click.echo(f"✗ No standard output file found for job {job_id}")
                sys.exit(1)
        except Exception as e:
            click.echo(f"✗ Error validating job {job_id}: {e}")
            sys.exit(1)
    else:
        # Follow the job output
        success, message = follow_job_output(job_id)

        if success:
            click.echo(f"✓ {message}")
            sys.exit(0)
        else:
            click.echo(f"✗ {message}")
            sys.exit(1)


if __name__ == "__main__":
    sfollow_cli()
