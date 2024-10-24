#tests for the create-checkout step of fre-make, for null_model.yaml
import os
from fre import fre
from pathlib import Path
from fre.pp import configure_script_yaml as csy
from click.testing import CliRunner

# Set what would be click options
experiment = "c96L65_am5f7b12r1_amip"
platform = "gfdl.ncrc5-intel22-classic"
target = "prod-openmp"

# Set example yaml paths, input directory
CWD = Path.cwd()
test_dir = Path("fre/make/tests/null_example")
test_yaml = Path(f"null_model.yaml")

# Set home for ~/cylc-src location in script
os.environ["HOME"]=str(Path(f"{CWD}/{test_dir}/configure_yaml_out"))

#run checkout command
runner = CliRunner()
result = runner.invoke(fre.fre, args=["make","create-checkout","-y","null_model.yaml","-p","ncrc5.intel","-t","debug"])

def test_checkout_script_exists():
    """
    Make sure checkout file exists
    """
    assert Path(f"/ncrc/home2/Avery.Kiihne/fremake_canopy/test/null_model_full/src/checkout.sh").exists()
def test_combined_yaml_exists():
    """
    Make sure combined yaml created
    """
    assert Path(f"{CWD}/{test_dir}/combined-null_model.yaml").exists()

