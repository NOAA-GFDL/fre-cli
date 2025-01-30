import os
from pathlib import Path
from fre.pp import configure_script_yaml as csy

# Set what would be click options
experiment = "c96L65_am5f7b12r1_amip"
platform = "gfdl.ncrc5-intel22-classic"
target = "prod-openmp"

# Set example yaml paths, input directory
CWD = Path.cwd()
test_dir = Path("fre/make/tests")
test_yaml = Path(f"null_example/null_model.yaml")

# Set home for ~/cylc-src location in script
os.environ["HOME"]=str(Path(f"{CWD}/{test_dir}/configure_yaml_out"))

def test_nullyaml_exists():
    """
    Make sure combined yaml file exists
    """
    assert Path(f"{CWD}/{test_dir}/{test_yaml}").exists()
def test_nullyaml_filled():
    """
    Make sure null.yaml is not an empty file
    """
    sum(1 for _ in open(f'{CWD}/{test_dir}/{test_yaml}')) > 1
