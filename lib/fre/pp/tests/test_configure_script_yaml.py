import os
from pathlib import Path
from fre.pp import configure_script_yaml as csy

# Set what would be click options
experiment = "c96L65_am5f7b12r1_amip"
platform = "gfdl.ncrc5-intel22-classic"
target = "prod-openmp"

# Set example yaml paths, input directory
CWD = Path.cwd()
test_dir = Path("fre/pp/tests")
test_yaml = Path(f"AM5_example/am5.yaml")

# Set home for ~/cylc-src location in script
os.environ["HOME"]=str(Path(f"{CWD}/{test_dir}/configure_yaml_out"))

def test_combinedyaml_exists():
    """
    Make sure combined yaml file exists
    """
    assert Path(f"{CWD}/{test_dir}/{test_yaml}").exists()

def test_configure_script():
    """ 
    Tests success of confgure yaml script
    Creates rose-suite, regrid rose-app, remap rose-app
    TO-DO: will break this up for better tests
    """
    os.chdir(f"{CWD}/{test_dir}/AM5_example")

    # Set output directory
    out_dir = Path(f"{os.getenv('HOME')}/cylc-src/{experiment}__{platform}__{target}")
    Path(out_dir).mkdir(parents=True,exist_ok=True)

    # Define combined yaml
    model_yaml = str(Path(f"{CWD}/{test_dir}/{test_yaml}"))

    # Invoke configure_yaml_script.py
    csy._yamlInfo(model_yaml,experiment,platform,target)

    # Check for configuration creation and final combined yaml
    assert all([Path(f"{out_dir}/{experiment}.yaml").exists(),
                Path(f"{out_dir}/rose-suite.conf").exists(),
                Path(f"{out_dir}/app/regrid-xy/rose-app.conf").exists(),
                Path(f"{out_dir}/app/remap-pp-components/rose-app.conf").exists()])

    # Go back to original directory
    os.chdir(CWD)
