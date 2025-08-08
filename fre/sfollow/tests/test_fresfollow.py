"""
Unit tests for the FRE SFollow CLI module

Tests cover the Click CLI interface for following SLURM job output.

authored by Tom Robinson
NOAA | GFDL
2025
"""

import unittest
from unittest.mock import patch
from click.testing import CliRunner

# Import the CLI components to test
from fre.sfollow.fresfollow import sfollow_cli


class TestSFollowCLI(unittest.TestCase):
    """
    Test cases for the sfollow CLI command.

    Tests the Click command line interface for the sfollow functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.

        Creates a Click CLI runner for testing commands.
        """
        self.runner = CliRunner()

    def test_sfollow_cli_help(self):
        """
        Test sfollow CLI help output.
        """
        result = self.runner.invoke(sfollow_cli, ['--help'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("follow SLURM job output in real-time", result.output)
        self.assertIn("JOB_ID", result.output)
        self.assertIn("--validate", result.output)

    @patch('fre.sfollow.fresfollow.follow_job_output')
    def test_sfollow_command_success(self, mock_follow_job_output):
        """
        Test successful execution of the sfollow command.
        
        :param mock_follow_job_output: Mocked follow_job_output function
        :type mock_follow_job_output: unittest.mock.Mock
        """
        mock_follow_job_output.return_value = (True, "Successfully followed job 12345 output")
        
        result = self.runner.invoke(sfollow_cli, ['12345'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("✓ Successfully followed job 12345 output", result.output)
        mock_follow_job_output.assert_called_once_with('12345')

    @patch('fre.sfollow.fresfollow.follow_job_output')
    def test_sfollow_command_failure(self, mock_follow_job_output):
        """
        Test failed execution of the sfollow command.
        
        :param mock_follow_job_output: Mocked follow_job_output function
        :type mock_follow_job_output: unittest.mock.Mock
        """
        mock_follow_job_output.return_value = (False, "Job not found")
        
        result = self.runner.invoke(sfollow_cli, ['99999'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("✗ Job not found", result.output)
        mock_follow_job_output.assert_called_once_with('99999')

    def test_sfollow_command_missing_job_id(self):
        """
        Test sfollow command with missing job ID argument.
        """
        result = self.runner.invoke(sfollow_cli, [])
        
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("missing argument", result.output.lower())

    @patch('fre.sfollow.sfollow.get_job_info')
    @patch('fre.sfollow.sfollow.parse_stdout_path')
    def test_sfollow_command_validate_success(self, mock_parse_stdout, mock_get_job_info):
        """
        Test successful validation mode.
        
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/path/to/output.log"
        mock_parse_stdout.return_value = "/path/to/output.log"
        
        result = self.runner.invoke(sfollow_cli, ['12345', '--validate'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("✓ Job 12345 found", result.output)
        self.assertIn("✓ Standard output file: /path/to/output.log", result.output)

    @patch('fre.sfollow.sfollow.get_job_info')
    @patch('fre.sfollow.sfollow.parse_stdout_path')
    def test_sfollow_command_validate_no_stdout(self, mock_parse_stdout, mock_get_job_info):
        """
        Test validation mode when no stdout file is found.
        
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/dev/null"
        mock_parse_stdout.return_value = None
        
        result = self.runner.invoke(sfollow_cli, ['12345', '--validate'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("✗ No standard output file found for job 12345", result.output)

    @patch('fre.sfollow.sfollow.get_job_info')
    def test_sfollow_command_validate_error(self, mock_get_job_info):
        """
        Test validation mode with error.
        
        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        mock_get_job_info.side_effect = Exception("SLURM error")
        
        result = self.runner.invoke(sfollow_cli, ['99999', '--validate'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn("✗ Error validating job 99999", result.output)

    def test_sfollow_command_with_short_validate_flag(self):
        """
        Test sfollow command with short validate flag.
        """
        with patch('fre.sfollow.sfollow.get_job_info') as mock_get_job_info, \
             patch('fre.sfollow.sfollow.parse_stdout_path') as mock_parse_stdout:
            mock_get_job_info.return_value = "JobId=12345\nStdOut=/path/to/output.log"
            mock_parse_stdout.return_value = "/path/to/output.log"
            
            result = self.runner.invoke(sfollow_cli, ['12345', '-v'])
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn("✓ Job 12345 found", result.output)


class TestSFollowCLIIntegration(unittest.TestCase):
    """
    Integration tests for the sfollow CLI.
    
    Tests the full command flow from CLI to core functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.
        
        Creates a Click CLI runner for testing commands.
        """
        self.runner = CliRunner()

    @patch('fre.sfollow.fresfollow.follow_job_output')
    def test_full_command_flow_success(self, mock_follow_job_output):
        """
        Test full command flow from CLI to core functionality.
        
        :param mock_follow_job_output: Mocked follow_job_output function
        :type mock_follow_job_output: unittest.mock.Mock
        """
        mock_follow_job_output.return_value = (True, "Successfully followed job 12345 output")
        
        # Test normal execution
        result = self.runner.invoke(sfollow_cli, ['12345'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("✓", result.output)
        
        # Verify the mock was called with correct arguments
        mock_follow_job_output.assert_called_once_with('12345')

    @patch('fre.sfollow.sfollow.get_job_info')
    @patch('fre.sfollow.sfollow.parse_stdout_path')
    def test_full_validation_flow(self, mock_parse_stdout, mock_get_job_info):
        """
        Test full validation flow from CLI to core functionality.
        
        :param mock_parse_stdout: Mocked parse_stdout_path function
        :type mock_parse_stdout: unittest.mock.Mock
        :param mock_get_job_info: Mocked get_job_info function
        :type mock_get_job_info: unittest.mock.Mock
        """
        mock_get_job_info.return_value = "JobId=12345\nStdOut=/path/to/output.log"
        mock_parse_stdout.return_value = "/path/to/output.log"
        
        # Test validation execution
        result = self.runner.invoke(sfollow_cli, ['12345', '--validate'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("✓ Job 12345 found", result.output)
        self.assertIn("✓ Standard output file:", result.output)
        
        # Verify the mocks were called
        mock_get_job_info.assert_called_once_with('12345')
        mock_parse_stdout.assert_called_once_with("JobId=12345\nStdOut=/path/to/output.log")


if __name__ == "__main__":
    unittest.main()
