"""
FRE SFollow - Monitor SLURM job output in real-time

This module provides functionality to follow the standard output of SLURM jobs.
It queries job information using scontrol and then follows the output file using less +F.

authored by Tom Robinson
NOAA | GFDL
2025
"""

import os
import subprocess
from typing import Optional, Tuple


def get_job_info(job_id: str) -> str:
    """
    Retrieve job information from SLURM using scontrol command.

    :param job_id: The SLURM job ID to query
    :type job_id: str
    :raises subprocess.CalledProcessError: If scontrol command fails
    :raises FileNotFoundError: If scontrol command is not found
    :return: Raw output from scontrol show jobid command
    :rtype: str

    .. note:: This function requires scontrol to be available in the system PATH
    """
    try:
        cmd = ["scontrol", "show", f"jobid={job_id}"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            f"Failed to get job information for job {job_id}: {e.stderr}"
        ) from e
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "scontrol command not found. Please ensure SLURM is installed and in PATH."
        ) from exc


def parse_stdout_path(scontrol_output: str) -> Optional[str]:
    """
    Parse the standard output file path from scontrol output.

    :param scontrol_output: Raw output from scontrol show jobid command
    :type scontrol_output: str
    :return: Path to the standard output file, or None if not found
    :rtype: Optional[str]

    .. note:: This function looks for lines containing 'StdOut=' and extracts the file path
    """
    for line in scontrol_output.split('\n'):
        line = line.strip()
        if line.startswith('StdOut='):
            # Split on '=' and take everything after the first '='
            parts = line.split('=', 1)
            if len(parts) == 2:
                stdout_path = parts[1].strip()
                # Handle case where path might be /dev/null or other special cases
                if stdout_path and stdout_path != '/dev/null':
                    return stdout_path
    return None


def follow_output_file(file_path: str) -> None:
    """
    Follow the output file using less +F command.

    :param file_path: Path to the file to follow
    :type file_path: str
    :raises FileNotFoundError: If the output file doesn't exist
    :raises subprocess.CalledProcessError: If less command fails

    .. note:: This function uses 'less +F' which follows the file and updates in real-time
    .. warning:: This function will block until the user exits less (typically with 'q')
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Output file not found: {file_path}")

    try:
        # Use less +F to follow the file
        subprocess.run(["less", "+F", file_path], check=True)
    except subprocess.CalledProcessError as e:
        raise subprocess.CalledProcessError(
            e.returncode,
            e.cmd,
            f"Failed to follow output file {file_path}"
        ) from e
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "less command not found. Please ensure less is installed and in PATH."
        ) from exc


def follow_job_output(job_id: str) -> Tuple[bool, str]:
    """
    Main function to follow a SLURM job's standard output.

    This function combines getting job information, parsing the stdout path,
    and following the output file.

    :param job_id: The SLURM job ID to follow
    :type job_id: str
    :return: Tuple of (success, message) indicating whether the operation succeeded
    :rtype: Tuple[bool, str]

    .. note:: This is the main entry point for the follow functionality
    """
    try:
        # Get job information
        job_info = get_job_info(job_id)

        # Parse stdout path
        stdout_path = parse_stdout_path(job_info)

        if stdout_path is None:
            return False, f"Could not find standard output file for job {job_id}"

        logging.info(f"Following output file: {stdout_path}")
        logging.info("Press 'q' to quit, Ctrl+C to interrupt following")

        # Follow the output file
        follow_output_file(stdout_path)

        return True, f"Successfully followed job {job_id} output"

    except subprocess.CalledProcessError as e:
        return False, f"SLURM error: {e}"
    except FileNotFoundError as e:
        return False, f"File error: {e}"
    except KeyboardInterrupt:
        return True, f"Following job {job_id} interrupted by user"
    except Exception as e:
        return False, f"Unexpected error: {e}"
