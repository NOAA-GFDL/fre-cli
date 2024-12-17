#tests for the create-checkout step of fre-make, for null_model.yaml
from pathlib import Path
import os
import subprocess
from fre.make import create_checkout_script

# Set example yaml paths, input directory
TEST_DIR = Path("fre/make/tests")
YAMLFILE = Path(f"{TEST_DIR}/null_example/null_model.yaml")

#set platform and target
PLATFORM = "ncrc5.intel"
TARGET = "debug"

#set output directory
#out_dir = Path(f"fre/make/tests/null_example/fre_make_out")
#Path(out_dir).mkdir(parents=True,exist_ok=True)

# Set home for ~/cylc-src location in script
#os.environ["HOME"]=str(Path(f"{out_dir}"))
OUT = f"{TEST_DIR}/checkout_out"
def_home = str(os.environ["HOME"]) 
os.environ["HOME"]=OUT#str(Path(OUT)) 

#run checkout command

def test_checkout_script_exists():
    """
    Make sure checkout file exists
    """
    result = create_checkout_script._checkout_create(YAMLFILE,PLATFORM,TARGET,no_parallel_checkout=False, jobs=False, verbose=False, execute=False)
    assert result.exit_code == 0
    assert Path(f"{HOME_DIR}/fremake_canopy/test/null_model_full/src/checkout.sh").exists()

def test_checkout_execute():
    """
    check if --execute option works
    """
    #subprocess.run(["rm","-rf",f"{out_dir}"])
    subprocess.run(["rm","-rf"])
    result = create_checkout_script._checkout_create(YAMLFILE,PLATFORM,TARGET,no_parallel_checkout=False, jobs=False, verbose=False, execute=False)
    assert (result.exit_code == 0)

