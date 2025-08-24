"""
Unit tests for the sfollow module

Tests cover the core functionality of following SLURM job output,
including job information retrieval, output parsing, and file following.

authored by Tom Robinson
NOAA | GFDL
2025
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess

# Import from the fre.sfollow module using absolute imports
from fre.sfollow.sfollow import (
    get_job_info,
    parse_stdout_path,
    follow_output_file,
    follow_job_output
)


class TestGetJobInfo(unittest.TestCase):
    """
    Test cases for the get_job_info function.

    Tests the function that retrieves job information from SLURM using scontrol.
    """

    @patch('subprocess.run')
    def test_get_job_info_success(self, mock_run):
        """
        Test successful job information retrieval.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        """
        # Mock successful scontrol output
        mock_result = MagicMock()
        mock_result.stdout = "JobId=12345 JobName=test_job\nStdOut=/path/to/output.log"
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        result = get_job_info("12345")

        self.assertEqual(result, "JobId=12345 JobName=test_job\nStdOut=/path/to/output.log")
        mock_run.assert_called_once_with(
            ["scontrol", "show", "jobid=12345"],
            capture_output=True,
            text=True,
            check=True
        )

    @patch('subprocess.run')
    def test_get_job_info_command_failure(self, mock_run):
        """
        Test handling of scontrol command failure.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        """
        # Mock failed scontrol command
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["scontrol", "show", "jobid=99999"], stderr="Job not found"
        )

        with self.assertRaises(subprocess.CalledProcessError) as context:
            get_job_info("99999")

        # Check that the exception contains the command that failed
        self.assertIn("scontrol", str(context.exception))

    @patch('subprocess.run')
    def test_get_job_info_command_not_found(self, mock_run):
        """
        Test handling when scontrol command is not found.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        """
        # Mock FileNotFoundError (command not found)
        mock_run.side_effect = FileNotFoundError("scontrol: command not found")

        with self.assertRaises(FileNotFoundError) as context:
            get_job_info("12345")

        self.assertIn("scontrol command not found", str(context.exception))


class TestParseStdoutPath(unittest.TestCase):
    """
    Test cases for the parse_stdout_path function.

    Tests the function that parses standard output file path from scontrol output.
    """

    def test_parse_stdout_path_success(self):
        """
        Test successful parsing of standard output path.
        """
        scontrol_output = """JobId=135549171 JobName=ESM4.5v06_om5b08_cobv3_meke_final_piC_2x0m15d_864x1a_2985x1o
   UserId=Thomas.Robinson(25002) GroupId=gfdl(500) MCS_label=N/A
   Priority=13113710 Nice=0 Account=gfdl_f QOS=normal
   JobState=RUNNING Reason=None Dependency=(null)
   StdOut=/gpfs/f5/gfdl_f/scratch/Thomas.Robinson/CMIP7/ESM4/DEV/ESM4.5v06_om5b08_cobv3_meke_final_piC/ncrc5.intel23-prod/stdout/run/ESM4.5v06_om5b08_cobv3_meke_final_piC_2x0m15d_864x1a_2985x1o.o135549171
   StdErr=/gpfs/f5/gfdl_f/scratch/Thomas.Robinson/CMIP7/ESM4/DEV/ESM4.5v06_om5b08_cobv3_meke_final_piC/ncrc5.intel23-prod/stdout/run/ESM4.5v06_om5b08_cobv3_meke_final_piC_2x0m15d_864x1a_2985x1o.o135549171"""

        expected_path = ("/gpfs/f5/gfdl_f/scratch/Thomas.Robinson/CMIP7/ESM4/DEV/"
                        "ESM4.5v06_om5b08_cobv3_meke_final_piC/ncrc5.intel23-prod/stdout/run/"
                        "ESM4.5v06_om5b08_cobv3_meke_final_piC_2x0m15d_864x1a_2985x1o.o135549171")

        result = parse_stdout_path(scontrol_output)
        self.assertEqual(result, expected_path)

    def test_parse_stdout_path_not_found(self):
        """
        Test parsing when StdOut line is not present.
        """
        scontrol_output = """JobId=12345 JobName=test_job
   UserId=user(1000) GroupId=group(1000)
   JobState=RUNNING Reason=None"""

        result = parse_stdout_path(scontrol_output)
        self.assertIsNone(result)

    def test_parse_stdout_path_dev_null(self):
        """
        Test parsing when StdOut is /dev/null.
        """
        scontrol_output = """JobId=12345 JobName=test_job
   StdOut=/dev/null
   StdErr=/dev/null"""

        result = parse_stdout_path(scontrol_output)
        self.assertIsNone(result)

    def test_parse_stdout_path_multiple_equals(self):
        """
        Test parsing when the output path contains equals signs.
        """
        scontrol_output = """JobId=12345 JobName=test_job
   StdOut=/path/to/file=with=equals.log
   StdErr=/dev/null"""

        result = parse_stdout_path(scontrol_output)
        self.assertEqual(result, "/path/to/file=with=equals.log")

    def test_parse_stdout_path_whitespace_handling(self):
        """
        Test parsing with various whitespace scenarios.
        """
        scontrol_output = """JobId=12345 JobName=test_job
   StdOut=/path/to/output.log
   StdErr=/dev/null"""

        result = parse_stdout_path(scontrol_output)
        self.assertEqual(result, "/path/to/output.log")


class TestFollowOutputFile(unittest.TestCase):
    """
    Test cases for the follow_output_file function.

    Tests the function that follows output files using less +F.
    """

    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_follow_output_file_success(self, mock_run, mock_exists):
        """
        Test successful file following.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        :param mock_exists: Mocked os.path.exists function
        :type mock_exists: unittest.mock.Mock
        """
        mock_exists.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        # Should not raise any exception
        follow_output_file("/path/to/output.log")

        mock_exists.assert_called_once_with("/path/to/output.log")
        mock_run.assert_called_once_with(["less", "+F", "/path/to/output.log"], check=True)

    @patch('os.path.exists')
    def test_follow_output_file_not_found(self, mock_exists):
        """
        Test handling when output file doesn't exist.

        :param mock_exists: Mocked os.path.exists function
        :type mock_exists: unittest.mock.Mock
        """
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError) as context:
            follow_output_file("/nonexistent/file.log")

        self.assertIn("Output file not found: /nonexistent/file.log", str(context.exception))

    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_follow_output_file_less_command_failure(self, mock_run, mock_exists):
        """
        Test handling when less command fails.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        :param mock_exists: Mocked os.path.exists function
        :type mock_exists: unittest.mock.Mock
        """
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["less", "+F", "/path/to/output.log"]
        )

        with self.assertRaises(subprocess.CalledProcessError) as context:
            follow_output_file("/path/to/output.log")

        # Check that the exception contains the command that failed
        self.assertIn("less", str(context.exception))

    @patch('os.path.exists')
    @patch('subprocess.run')
    def test_follow_output_file_less_not_found(self, mock_run, mock_exists):
        """
        Test handling when less command is not found.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        :param mock_exists: Mocked os.path.exists function
        :type mock_exists: unittest.mock.Mock
        """
        mock_exists.return_value = True
        mock_run.side_effect = FileNotFoundError("less: command not found")

        with self.assertRaises(FileNotFoundError) as context:
            follow_output_file("/path/to/output.log")

        self.assertIn("less command not found", str(context.exception))


class TestFollowJobOutput(unittest.TestCase):
    """
    Test cases for the follow_job_output function.

    Tests the main function that combines all follow functionality.
    """

    @patch('fre.sfollow.sfollow.follow_output_file')
    @patch('fre.sfollow.sfollow.parse_stdout_path')
    @patch('fre.sfollow.sfollow.get_job_info')
    def test_follow_job_output_success(self, mock_get_job_info, mock_parse_stdout, mock_follow_file):
        """
        Test successful end-to-end job following.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        :param mock_follow_file: Mocked follow_output_file function
        :type mock_follow_file: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/path/to/output.log"
        mock_parse_stdout.return_value = "/path/to/output.log"
        mock_follow_file.return_value = None

        success, message = follow_job_output("12345")

        self.assertTrue(success)
        self.assertIn("Successfully followed job 12345 output", message)
        mock_get_job_info.assert_called_once_with("12345")
        mock_parse_stdout.assert_called_once_with("JobId=12345\nStdOut=/path/to/output.log")
        mock_follow_file.assert_called_once_with("/path/to/output.log")

    @patch('fre.sfollow.sfollow.parse_stdout_path')
    @patch('fre.sfollow.sfollow.get_job_info')
    def test_follow_job_output_no_stdout(self, mock_get_job_info, mock_parse_stdout):
        """
        Test handling when no stdout file is found.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/dev/null"
        mock_parse_stdout.return_value = None

        success, message = follow_job_output("12345")

        self.assertFalse(success)
        self.assertIn("Could not find standard output file for job 12345", message)

    @patch('fre.sfollow.sfollow.get_job_info')
    def test_follow_job_output_slurm_error(self, mock_get_job_info):
        """
        Test handling of SLURM errors.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        mock_get_job_info.side_effect = subprocess.CalledProcessError(
            1, ["scontrol"], "Job not found"
        )

        success, message = follow_job_output("99999")

        self.assertFalse(success)
        self.assertIn("SLURM error:", message)

    @patch('fre.sfollow.sfollow.follow_output_file')
    @patch('fre.sfollow.sfollow.parse_stdout_path')
    @patch('fre.sfollow.sfollow.get_job_info')
    def test_follow_job_output_keyboard_interrupt(self, mock_get_job_info, mock_parse_stdout, mock_follow_file):
        """
        Test handling of keyboard interrupt during following.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        :param mock_follow_file: Mocked follow_output_file function
        :type mock_follow_file: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/path/to/output.log"
        mock_parse_stdout.return_value = "/path/to/output.log"
        mock_follow_file.side_effect = KeyboardInterrupt()

        success, message = follow_job_output("12345")

        self.assertTrue(success)
        self.assertIn("Following job 12345 interrupted by user", message)

    @patch('fre.sfollow.sfollow.get_job_info')
    def test_follow_job_output_unexpected_error(self, mock_get_job_info):
        """
        Test handling of unexpected errors.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        mock_get_job_info.side_effect = Exception("Unexpected error occurred")

        success, message = follow_job_output("12345")

        self.assertFalse(success)
        self.assertIn("Unexpected error:", message)

    @patch('fre.sfollow.sfollow.follow_output_file')
    @patch('fre.sfollow.sfollow.parse_stdout_path')
    @patch('fre.sfollow.sfollow.get_job_info')
    def test_follow_job_output_file_error(self, mock_get_job_info, mock_parse_stdout, mock_follow_file):
        """
        Test handling when file following fails with FileNotFoundError.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        :param mock_follow_file: Mocked follow_output_file function
        :type mock_follow_file: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/path/to/output.log"
        mock_parse_stdout.return_value = "/path/to/output.log"
        mock_follow_file.side_effect = FileNotFoundError("Output file not found: /path/to/output.log")

        success, message = follow_job_output("12345")

        self.assertFalse(success)
        self.assertIn("File error:", message)

    def test_parse_stdout_path_empty_input(self):
        """
        Test parsing with empty input.
        """
        # Test empty string
        result = parse_stdout_path("")
        self.assertIsNone(result)

    def test_parse_stdout_path_malformed_output(self):
        """
        Test parsing with malformed scontrol output.
        """
        # Test with StdOut= but no actual path
        scontrol_output = """JobId=12345 JobName=test_job
   StdOut=
   StdErr=/dev/null"""

        result = parse_stdout_path(scontrol_output)
        self.assertIsNone(result)

        # Test with StdOut= followed by whitespace only
        scontrol_output = """JobId=12345 JobName=test_job
   StdOut=
   StdErr=/dev/null"""

        result = parse_stdout_path(scontrol_output)
        self.assertIsNone(result)


class TestErrorHandlingIntegration(unittest.TestCase):
    """
    Additional tests specifically focused on error handling integration.

    These tests verify that errors are properly propagated and handled
    throughout the entire call chain.
    """

    @patch('subprocess.run')
    def test_real_error_message_propagation(self, mock_run):
        """
        Test that actual error messages are properly preserved and propagated.

        :param mock_run: Mocked subprocess.run function
        :type mock_run: unittest.mock.Mock
        """
        # Test specific SLURM error message propagation
        error_message = "slurm_load_jobs error: Invalid job id specified"
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["scontrol", "show", "jobid=invalid"], stderr=error_message
        )

        success, message = follow_job_output("invalid")

        self.assertFalse(success)
        self.assertIn("SLURM error:", message)

    def test_empty_job_id_handling(self):
        """
        Test handling of empty job IDs.
        """
        # Test empty string
        success, _message = follow_job_output("")
        self.assertFalse(success)

    @patch('fre.sfollow.sfollow.get_job_info')
    def test_network_timeout_simulation(self, mock_get_job_info):
        """
        Test handling of network timeouts or hanging commands.

        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        # Simulate a timeout error
        mock_get_job_info.side_effect = subprocess.TimeoutExpired(
            ["scontrol", "show", "jobid=12345"], timeout=30
        )

        success, message = follow_job_output("12345")

        self.assertFalse(success)
        # TimeoutExpired is caught as an unexpected error, which is correct behavior
        self.assertIn("Unexpected error:", message)
        self.assertIn("timed out", message)


if __name__ == "__main__":
    unittest.main()
