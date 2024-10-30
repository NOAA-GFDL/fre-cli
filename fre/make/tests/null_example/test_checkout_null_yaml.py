#tests for the create-checkout step of fre-make, for null_model.yaml
import os
from fre import fre
from pathlib import Path
from fre.pp import configure_script_yaml as csy
from click.testing import CliRunner
import subprocess
from fre.make import createCheckout

# Set example yaml paths, input directory
CWD = Path.cwd()
test_dir = Path("fre/make/tests/null_example")
test_yaml = Path(f"null_model.yaml")

#set platform and target
platform = "ncrc5.intel"
target = "debug"
yamlfile = "null_model.yaml"

# Set home for ~/cylc-src location in script
os.environ["HOME"]=str(Path(f"{CWD}/{test_dir}/configure_yaml_out"))

#run checkout command
runner = CliRunner()

# Set output directory
out_dir = Path(f"{os.getenv('HOME'/fremake_canopy/test/null_model_full/src)}")
Path(out_dir).mkdir(parents=True,exist_ok=True)
def test_checkout_script_exists():
    """
    Make sure checkout file exists
    """
    result = runner.invoke(fre.fre, args=["make","create-checkout","-y","null_model.yaml","-p","ncrc5.intel","-t","debug"])
    #createCheckout.checkout_create(["null_model.yaml","ncrc5.intel","debug"])
    assert Path(f"{out_dir}/checkout.sh").exists()

def test_checkout_execute():
    """
    check if --execute option works
    """
    subprocess.run(["rm","-rf","/ncrc/home2/Avery.Kiihne/fremake_canopy/test/null_model_full/src/"])
    result = runner.invoke(fre.fre, args=["make","create-checkout","-y","null_model.yaml","-p","ncrc5.intel","-t","debug","--execute"])
    assert (result.exit_code == 0)

