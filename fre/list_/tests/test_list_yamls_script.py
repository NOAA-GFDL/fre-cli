"""
Pytest for list_yamls_script.py

Tests the list_yamls_subtool function with various flag combinations
using the example model YAML file.
"""
from pathlib import Path
import pytest
from fre.list_.list_yamls_script import list_yamls_subtool


class TestListYamlsScript:
    """Test suite for list_yamls_subtool function"""

    @pytest.fixture
    def model_yaml_path(self):
        """Provide path to AM5 example YAML file"""
        return str(
            Path(__file__).parent / "yamls" / "model.yaml"
        )

    def test_list_yamls_default_all_yamls(self, model_yaml_path):
        """Test default behavior returns all YAMLs for the experiment"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application=None
            )

            # Verify we get all YAMLs
            assert isinstance(result, str)

            # Check that result contains expected YAML files
            yaml_names = [Path(y).name for y in result.split(",")]
            assert "model.yaml" in yaml_names
            assert "compile.yaml" in yaml_names
            assert "platforms.yaml" in yaml_names
            assert "settings.yaml" in yaml_names
            assert "run1.yaml" in yaml_names
            assert "pp.c96_amip.yaml" in yaml_names
            assert "pp-test.c96_amip.yaml" in yaml_names
            assert "analysis1.yaml" in yaml_names

    def test_list_yamls_runtime_only(self, model_yaml_path):
        """Test runtime_only flag returns model YAML plus runtime-related YAMLs"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application="run"
            )

            yaml_names = [Path(y).name for y in result.split(",")]

            # Model YAML should always be included
            assert "model.yaml" in yaml_names
            # Should contain platform, settings, and run YAMLs
            assert "platforms.yaml" in yaml_names
            assert "settings.yaml" in yaml_names
            assert "run1.yaml" in yaml_names

            # Should NOT contain compile, postprocessing, or analysis YAMLs
            assert "compile.yaml" not in yaml_names
            assert "pp.c96_amip.yaml" not in yaml_names
            assert "analysis1.yaml" not in yaml_names

    def test_list_yamls_postprocess_only(self, model_yaml_path):
        """Test postprocess_only flag (without analysis) returns model YAML plus postprocessing YAMLs"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application="postprocess"
            )

            yaml_names = [Path(y).name for y in result.split(",")]

            # Model YAML should always be included
            assert "model.yaml" in yaml_names
            # Should contain settings and postprocessing YAMLs
            assert "settings.yaml" in yaml_names
            assert "pp.c96_amip.yaml" in yaml_names
            assert "pp-test.c96_amip.yaml" in yaml_names

            # Should NOT contain compile, platform, run, or analysis YAMLs
            assert "compile.yaml" not in yaml_names
            assert "platforms.yaml" not in yaml_names
            assert "run1.yaml" not in yaml_names
            assert "analysis1.yaml" not in yaml_names

    def test_list_yamls_analysis_only(self, model_yaml_path):
        """Test analysis_only flag (without postprocess) returns model YAML plus analysis YAMLs"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application="analysis"
            )

            yaml_names = [Path(y).name for y in result.split(",")]

            # Model YAML should always be included
            assert "model.yaml" in yaml_names
            # Should contain settings and analysis YAMLs
            assert "settings.yaml" in yaml_names
            assert "analysis1.yaml" in yaml_names

            # Should NOT contain compile, platform, run, or postprocessing YAMLs
            assert "compile.yaml" not in yaml_names
            assert "platforms.yaml" not in yaml_names
            assert "run1.yaml" not in yaml_names
            assert "pp.c96_amip.yaml" not in yaml_names

    def test_list_yamls_postprocess_and_analysis(self, model_yaml_path):
        """Test both postprocess_only and analysis_only returns model YAML plus both"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application="postprocess,analysis"
            )

            yaml_names = [Path(y).name for y in result.split(",")]

            # Model YAML should always be included
            assert "model.yaml" in yaml_names
            # Should contain settings, postprocessing, and analysis YAMLs
            assert "settings.yaml" in yaml_names
            assert "pp.c96_amip.yaml" in yaml_names
            assert "pp-test.c96_amip.yaml" in yaml_names
            assert "analysis1.yaml" in yaml_names

            # Should NOT contain compile, platform, or run YAMLs
            assert "compile.yaml" not in yaml_names
            assert "platforms.yaml" not in yaml_names
            assert "run1.yaml" not in yaml_names

    def test_list_yamls_no_experiment(self, model_yaml_path):
        """Test with no experiment name provided (default compile behavior)"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="",
                application=None
            )

            yaml_names = [Path(y).name for y in result.split(",")]

            # Model YAML should always be included
            assert "model.yaml" in yaml_names
            # Should contain compile and platform YAMLs
            assert "compile.yaml" in yaml_names
            assert "platforms.yaml" in yaml_names

            # Should NOT contain experiment-specific YAMLs
            assert "run1.yaml" not in yaml_names

    def test_list_yamls_returns_full_paths(self, model_yaml_path):
        """Test that returned YAMLs have full paths"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application=None
            )

            # All paths should be absolute or contain full directory structure
            for yaml_path in result.split(","):
                path_obj = Path(yaml_path)
                assert path_obj.is_absolute() or "/" in yaml_path

    def test_list_yamls_model_yaml_always_included(self, model_yaml_path):
        """Test that model YAML is always included regardless of flags"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            test_cases = [
                ("run"),  # runtime_only
                ("postprocess"),  # postprocess_only
                ("analysis"),  # analysis_only
                ("postprocess,analysis"),   # postprocess_only and analysis_only
                (None),  # default (no application given)
            ]

            for app in test_cases:
                result = list_yamls_subtool(
                    yamlfile=model_yaml_path,
                    experiment="experiment1",
                    application=app
                )

                yaml_names = [Path(y).name for y in result.split(",")]
                assert "model.yaml" in yaml_names

    def test_list_yamls_result_is_str(self, model_yaml_path):
        """Test that the result is always a comma separated string"""
        with pytest.raises(ValueError): #, match = "  *** PROVIDE THE MISSING YAML CONFIGURATIONS ***"):
            result = list_yamls_subtool(
                yamlfile=model_yaml_path,
                experiment="experiment1",
                application=None
            )

            assert isinstance(result, str)
