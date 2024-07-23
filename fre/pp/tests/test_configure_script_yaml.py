import os
from pathlib import Path
from fre.pp import configure_script_yaml as csy

# Set ex. yaml paths, input directory, output directory
CWD = Path.cwd()
yamls_dir = Path("tests/example_ppyamls")
in_dir = Path(f"{CWD}/{yamls_dir}")

# Set what would be click options
experiment = "c96L65_am5f7b12r1_amip"
platform = "gfdl.ncrc5-intel22-classic"
target = "prod-openmp"

# Set home for ~/cylc-src location in script
os.environ["HOME"]=str(Path(f"{CWD}/{yamls_dir}/yaml_out"))

def test_mainyaml_exists():
    """
    Make sure main yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/am5.yaml").exists()

def test_expyaml_exists():
    """
    Make sure experiment yaml file exists
    """
    assert Path(f"{CWD}/{yamls_dir}/yaml_include/pp.c96_amip.yaml").exists()

def test_configure_script():
    """ 
    Tests success of confgure yaml script
    Creates rose-suite, regrid rose-app, remap rose-app
    TO-DO: will break this up for better tests
    """
    # Go into example yamls location
    os.chdir(in_dir)

    # Set output directory
    out_dir = Path(f"{os.getenv('HOME')}/cylc-src/{experiment}__{platform}__{target}")
    Path(out_dir).mkdir(parents=True,exist_ok=True)

    # Define main yaml
    mainyaml = str(Path(f"{CWD}/{yamls_dir}/am5.yaml"))

    # Invoke configure_yaml_script.py
    csy._yamlInfo(mainyaml,experiment,platform,target)

    # Check for configuration creation and final combined yaml
    assert all([Path(f"{Path.cwd()}/yaml_out/cylc-src/{experiment}__{platform}__{target}/{experiment}.yaml").exists(),
                Path(f"{Path.cwd()}/yaml_out/cylc-src/{experiment}__{platform}__{target}/rose-suite.conf").exists(),
                Path(f"{Path.cwd()}/yaml_out/cylc-src/{experiment}__{platform}__{target}/app/regrid-xy/rose-app.conf").exists(),
                Path(f"{Path.cwd()}/yaml_out/cylc-src/{experiment}__{platform}__{target}/app/remap-pp-components/rose-app.conf").exists()])
