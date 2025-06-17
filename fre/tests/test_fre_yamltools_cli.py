''' test "fre yamltools" calls '''

import yaml
from pathlib import Path

from click.testing import CliRunner

from fre import fre

runner = CliRunner()


def test_cli_fre_yamltools():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools"])
    assert result.exit_code == 0


def test_cli_fre_yamltools_help():
    ''' fre yamltools --help '''
    result = runner.invoke(fre.fre, args=["yamltools", "--help"])
    assert result.exit_code == 0


def test_cli_fre_yamltools_opt_dne():
    ''' fre yamltools optionDNE '''
    result = runner.invoke(fre.fre, args=["yamltools", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_yamltools_combine_help():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls"])
    assert result.exit_code == 0


def test_cli_fre_yamltools_combine_help():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls", "--help"])
    assert result.exit_code == 0


def test_cli_fre_yamltools_combine_opt_dne():
    ''' fre yamltools '''
    result = runner.invoke(fre.fre, args=["yamltools", "combine-yamls", "optionDNE"])
    assert result.exit_code == 2


FAKE_AM5_EX_DIR = "fre/yamltools/tests/AM5_example"


def test_cli_fre_yamltools_combine_cmoryaml():
    ''' fre yamltools combine-yamls for cmorization'''
    output_combined_cmor_yaml = f"{FAKE_AM5_EX_DIR}/FOO_cmor.yaml"
    if Path(output_combined_cmor_yaml).exists():
        Path(output_combined_cmor_yaml).unlink()

    result = runner.invoke(fre.fre, args=["-v", "-v", "yamltools", "combine-yamls",
                                          "-y", f"{FAKE_AM5_EX_DIR}/am5.yaml",
                                          "-e", "c96L65_am5f7b12r1_amip",
                                          "-p", "ncrc5.intel",
                                          "-t", "prod-openmp",
                                          "--use", "cmor", "--output", output_combined_cmor_yaml])
    assert all([result.exit_code == 0,
                Path(output_combined_cmor_yaml).exists()
                ])

    compare_combined_cmor_yaml = f"{FAKE_AM5_EX_DIR}/COMPARE_TEST_OUTPUT_cmor.yaml"
    assert Path(compare_combined_cmor_yaml).exists()
    comp_file_output = open(compare_combined_cmor_yaml, 'r')
    comp_file_output_data = yaml.load(comp_file_output, Loader=yaml.SafeLoader)

    file_output = open(output_combined_cmor_yaml, 'r')
    file_output_data = yaml.load(file_output, Loader=yaml.SafeLoader)

    assert file_output_data == comp_file_output_data
