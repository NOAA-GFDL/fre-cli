"""Tests for validating FRE YAML files before they are combined."""

from pathlib import Path

import pytest

from fre.yamltools.validation import YamlKind, validate_yaml_file, validate_yaml_inputs


TEST_DIR = Path("fre/yamltools/tests/AM5_example")


@pytest.mark.parametrize(
    ("relative_path", "kind"),
    [
        ("am5.yaml", YamlKind.MODEL),
        ("compile_yamls/compile.yaml", YamlKind.COMPILE),
        ("compile_yamls/platforms.yaml", YamlKind.PLATFORMS),
        ("pp_yamls/pp.c96_amip.yaml", YamlKind.PP),
        ("analysis_yamls/clouds.yaml", YamlKind.ANALYSIS),
        ("cmor_yamls/cmor.am5.yaml", YamlKind.CMOR),
        ("grid_yamls/TEST_grids.yaml", YamlKind.GRIDS),
        ("settings.yaml", YamlKind.SETTINGS),
    ],
)
def test_each_yaml_kind_accepts_current_example(relative_path, kind):
    """Every current example follows its kind's top-level convention."""
    validate_yaml_file(TEST_DIR / relative_path, kind)


def test_validation_does_not_resolve_cross_file_aliases():
    """An input can be validated while its aliases are still unresolved."""
    validate_yaml_file(TEST_DIR / "compile_yamls/compile.yaml", YamlKind.COMPILE)


def test_invalid_kind_reports_unexpected_top_level_key(tmp_path):
    """A file with another kind's key is rejected before combination."""
    compile_yaml = tmp_path / "compile.yaml"
    compile_yaml.write_text("postprocess: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing top-level key.*compile"):
        validate_yaml_file(compile_yaml, YamlKind.COMPILE)


def test_invalid_top_level_value_type_is_reported(tmp_path):
    """Top-level collections must have the shape required by their kind."""
    platforms_yaml = tmp_path / "platforms.yaml"
    platforms_yaml.write_text("platforms: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a sequence, not a mapping"):
        validate_yaml_file(platforms_yaml, YamlKind.PLATFORMS)


def test_duplicate_top_level_key_is_reported(tmp_path):
    """Duplicate top-level keys cannot silently overwrite one another."""
    pp_yaml = tmp_path / "pp.yaml"
    pp_yaml.write_text("postprocess: {}\npostprocess: {}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate top-level key 'postprocess'"):
        validate_yaml_file(pp_yaml, YamlKind.PP)


def test_validate_compile_inputs_follows_model_references():
    """Compile validation follows both paths in the model's build section."""
    validate_yaml_inputs(TEST_DIR / "am5.yaml", "am5", "compile")


def test_validate_pp_inputs_follows_selected_experiment_references():
    """PP validation follows settings, PP, and analysis references."""
    validate_yaml_inputs(
        TEST_DIR / "am5.yaml",
        "c96L65_am5f7b12r1_amip",
        "pp",
    )
