"""
Tests for fre run functionality, based on original FRE frerun tests
"""

import pytest
from click.testing import CliRunner
from fre.run.frerun import run_cli
from fre.run.run_script import run_script_subtool


class TestFrerunBasics:
    """Test basic frerun functionality similar to original FRE tests"""
    
    def setup_method(self):
        """Setup for each test"""
        self.runner = CliRunner()
    
    def test_frerun_help(self):
        """Test frerun print help message (based on original frerun.bats test)"""
        result = self.runner.invoke(run_cli, ['--help'])
        assert result.exit_code == 0
        assert "run subcommands" in result.output
    
    def test_frerun_run_help(self):
        """Test fre run run --help"""
        result = self.runner.invoke(run_cli, ['run', '--help'])
        assert result.exit_code == 0
        assert "Execute fre run workflow" in result.output
        assert "--platform" in result.output
        assert "--experiment" in result.output
    
    def test_frerun_missing_experiment(self):
        """Test error when no experiment specified (based on original frerun.bats test)"""
        result = self.runner.invoke(run_cli, ['run'])
        assert result.exit_code == 1
        # Should get error about missing experiment
    
    def test_frerun_missing_platform(self):
        """Test error when no platform specified"""
        result = self.runner.invoke(run_cli, ['run', '--experiment', 'test_exp'])
        assert result.exit_code == 1
        # Should get error about missing platform
    
    def test_frerun_with_valid_params(self):
        """Test successful run with valid parameters"""
        result = self.runner.invoke(run_cli, ['run', 
                                             '--platform', 'test_platform',
                                             '--experiment', 'test_experiment',
                                             '--target', 'prod'])
        assert result.exit_code == 0
    
    def test_frerun_with_submit_flag(self):
        """Test run with submit flag"""
        result = self.runner.invoke(run_cli, ['run',
                                             '--platform', 'test_platform', 
                                             '--experiment', 'test_experiment',
                                             '--submit'])
        assert result.exit_code == 0
    
    def test_frerun_with_staging_flag(self):
        """Test run with staging flag"""
        result = self.runner.invoke(run_cli, ['run',
                                             '--platform', 'test_platform',
                                             '--experiment', 'test_experiment', 
                                             '--staging'])
        assert result.exit_code == 0


class TestRunScriptSubtool:
    """Test the run_script_subtool function directly"""
    
    def test_run_script_subtool_missing_experiment(self):
        """Test run_script_subtool with missing experiment"""
        with pytest.raises(ValueError, match="Experiment name is required"):
            run_script_subtool(platform="test_platform")
    
    def test_run_script_subtool_missing_platform(self):
        """Test run_script_subtool with missing platform"""
        with pytest.raises(ValueError, match="Platform is required"):
            run_script_subtool(experiment="test_experiment")
    
    def test_run_script_subtool_success(self):
        """Test successful run_script_subtool execution"""
        result = run_script_subtool(platform="test_platform", 
                                  experiment="test_experiment",
                                  target="prod")
        assert result is True
    
    def test_run_script_subtool_with_flags(self):
        """Test run_script_subtool with submit and staging flags"""
        result = run_script_subtool(platform="test_platform",
                                  experiment="test_experiment", 
                                  submit=True,
                                  staging=True)
        assert result is True


class TestFrerunLegacyCompatibility:
    """Test backward compatibility with existing functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.runner = CliRunner()
    
    def test_function_command_still_works(self):
        """Test that the original function command still works"""
        result = self.runner.invoke(run_cli, ['function'])
        assert result.exit_code == 1  # Still raises NotImplementedError
        
    def test_function_command_uppercase_still_works(self):
        """Test that the original function command with uppercase still works"""
        result = self.runner.invoke(run_cli, ['function', '--uppercase'])
        assert result.exit_code == 1  # Still raises NotImplementedError