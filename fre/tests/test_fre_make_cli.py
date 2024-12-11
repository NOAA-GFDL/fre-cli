''' test "fre make" calls '''

from click.testing import CliRunner
from pathlib import Path
import os
from fre import fre

runner = CliRunner()

def test_cli_fre_make():
    ''' fre make '''
    result = runner.invoke(fre.fre, args=["make"])
    assert result.exit_code == 0

def test_cli_fre_make_help():
    ''' fre make --help '''
    result = runner.invoke(fre.fre, args=["make", "--help"])
    assert result.exit_code == 0

def test_cli_fre_make_opt_dne():
    ''' fre make optionDNE '''
    result = runner.invoke(fre.fre, args=["make", "optionDNE"])
    assert result.exit_code == 2

def test_cli_fre_make_create_checkout_baremetal():
    ''' fre make create-checkout -y am5.yaml -p ncrc5.intel23 -t debug'''
    # Set paths and click options
    test_dir = Path("fre/tests")
    yamlfile = Path("fre/make/tests/null_example")
    platform = "ncrc5.intel23"
    target = "debug"

    # Create output path to test that files exist
    out_path=f"{test_dir}/fremake_out"
    Path(out_path).mkdir(parents=True,exist_ok=True)

    # Set HOME for modelRoot location (output location) in fre make
    os.environ["HOME"]=str(Path(out_path))
    
    # run create-checkout
    result = runner.invoke(fre.fre, args=["make", "create-checkout", "-y", f"{yamlfile}/null_model.yaml", "-p", platform, "-t", target])

    # Check for successful command, creation of checkout script, and that script is executable (os.access - checks is file has specific access mode, os.X_OK - checks executable permission)
    assert all ([result.exit_code == 0,
                 Path(f"{out_path}/fremake_canopy/test/null_model_full/src/checkout.sh").exists(),
                 os.access(Path(f"{out_path}/fremake_canopy/test/null_model_full/src/checkout.sh"), os.X_OK)])

def test_cli_fre_make_create_checkout_container():
    ''' fre make create-checkout -y am5.yaml -p hpcme.2023 -t debug'''
    # Set paths and click options
    test_dir = Path("fre/tests")
    yamlfile = Path("fre/make/tests/AM5_example/")
    platform = "hpcme.2023"
    target = "debug"

    # run create-checkout
    result = runner.invoke(fre.fre, args=["make", "create-checkout", "-y", f"{yamlfile}/am5.yaml", "-p", platform, "-t", target])

    # Check for successful command, creation of checkout script, and that script is executable (os.access - checks is file has specific access mode, os.X_OK - checks executable permission)
    assert all ([result.exit_code == 0,
                 Path(f"tmp/{platform}/checkout.sh").exists(),
                 os.access(Path(f"tmp/{platform}/checkout.sh"), os.X_OK) == False ])
