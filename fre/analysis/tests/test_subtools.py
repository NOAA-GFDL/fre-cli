from pathlib import Path
import pytest
from subprocess import CalledProcessError
from tempfile import TemporaryDirectory

#from analysis_scripts import available_plugins, UnknownPluginError
from analysis_scripts import UnknownPluginError
from fre.analysis.subtools import install_analysis_package, list_plugins, run_analysis


def make_experiment_yaml(path, name, whitespace="  "):
    """Creates and experiment yaml configuration file for testing.

    Args:
        path: Path to the experiment yaml file that will be created.
        name: String name of the analysis package.
        whitespace: Amount of whitespace each block will be indented by.
    """
    with open(path, "w") as yaml_:
        yaml_.write("analysis:\n")
        yaml_.write(f"{whitespace}{name}:\n")
        yaml_.write(f"{2*whitespace}required:\n")
        yaml_.write(f"{3*whitespace}arg: value\n")

## DO NOT MERGE THIS, avoiding local testing issue w/ intake-esm...
#@pytest.mark.skip(reason='intake-esm threading issue, related to env var ITK_ESM_THREADING. ' + \
#                         'see https://github.com/NOAA-GFDL/analysis-scripts/issues/26 for more info' )
def test_install_analysis_package():
    """Tests installing an analysis package."""
    url = "github.com/noaa-gfdl/analysis-scripts"
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        install_analysis_package(url, name, tmp)
        #plugins = list_plugins(tmp)
        assert name in list_plugins(tmp)


## DO NOT MERGE THIS, avoiding local testing issue w/ intake-esm...
#@pytest.mark.skip(reason='intake-esm threading issue, related to env var ITK_ESM_THREADING. ' + \
#                         'see https://github.com/NOAA-GFDL/analysis-scripts/issues/26 for more info' )
def test_run_analysis():
    """Tests running an analysis package.  Expects to fail because we don't make a catalog."""
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        make_experiment_yaml(experiment_yaml, name)
        library_directory = Path(tmp) / "env"
        url = "github.com/noaa-gfdl/analysis-scripts"
        catalog = Path(tmp) / "fake-catalog"
        install_analysis_package(url, name, library_directory)
        with pytest.raises(CalledProcessError) as err:
            run_analysis(name, str(catalog), ".", "output.yaml", experiment_yaml,
                    library_directory)
        for line in err._excinfo[1].output.decode("utf-8").split("\n"):
            if f"No such file or directory: '{str(catalog)}'" in line:
                return
        assert False

## DO NOT MERGE THIS, avoiding local testing issue w/ intake-esm...
#@pytest.mark.skip(reason='intake-esm threading issue, related to env var ITK_ESM_THREADING. ' + \
#                         'see https://github.com/NOAA-GFDL/analysis-scripts/issues/26 for more info' )
def test_run_unknown_analysis():
    """Get an UnknownPluginError when trying to run an uninstalled package."""
    name = "freanalysis_clouds"
    with TemporaryDirectory() as tmp:
        experiment_yaml = Path(tmp) / "experiment.yaml"
        make_experiment_yaml(experiment_yaml, name)
        with pytest.raises(UnknownPluginError) as err:
            run_analysis(name, "fake-catalog", ".", "output.yaml", experiment_yaml)
