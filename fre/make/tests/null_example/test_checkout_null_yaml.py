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
yamlfile = Path(f"{test_dir}/null_model.yaml")

#set platform and target
platform = "ncrc5.intel"
target = "debug"

#set output directory
out_dir = Path(f"{os.getenv('HOME')}/fre_make_out")
Path(out_dir).mkdir(parents=True,exist_ok=True)

# Set home for ~/cylc-src location in script
os.environ["HOME"]=str(Path(f"{out_dir}"))

#run checkout command
runner = CliRunner()

def test_checkout_script_exists():
    """
    Make sure checkout file exists
    """
    result = runner.invoke(fre.fre, args=["make","create-checkout","-y",yamlfile,"-p",platform,"-t",target])
    #createCheckout.checkout_create(["null_model.yaml","ncrc5.intel","debug"])
    assert result.exit_code == 0
    assert Path(f"{out_dir}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()

def test_checkout_execute():
    """
    check if --execute option works
    """
    subprocess.run(["rm","-rf",f"{out_dir}"])
    result = runner.invoke(fre.fre, args=["make","create-checkout","-y",yamlfile,"-p",platform,"-t",target,"--execute"])
    assert (result.exit_code == 0)

