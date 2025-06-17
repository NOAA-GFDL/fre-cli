"""test "fre make" calls"""

from click.testing import CliRunner
from pathlib import Path
import os
import shutil
from fre import fre

runner = CliRunner()
TEST_DIR = Path("fre/tests")
OUT_PATH_BASE = f"{TEST_DIR}/test_files/test_fre_make_cli"


def test_cli_fre_make():
    """fre make"""
    result = runner.invoke(fre.fre, args=["make"])
    assert result.exit_code == 0


def test_cli_fre_make_help():
    """fre make --help"""
    result = runner.invoke(fre.fre, args=["make", "--help"])
    assert result.exit_code == 0


def test_cli_fre_make_opt_dne():
    """fre make optionDNE"""
    result = runner.invoke(fre.fre, args=["make", "optionDNE"])
    assert result.exit_code == 2


def test_cli_fre_make_create_checkout_baremetal():
    """fre make checkout -y am5.yaml -p ncrc5.intel23 -t debug"""
    OUT_PATH = f"{OUT_PATH_BASE}/fremake_out_baremetal"

    # Set paths and click options
    yamlfile = Path("fre/make/tests/null_example/")
    platform = "ncrc5.intel23"
    target = "debug"

    # Delete existing checkout.sh if it exists
    if Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh").exists():
        Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh").unlink()

    # Create output path to test that files exist
    Path(OUT_PATH).mkdir(parents=True, exist_ok=True)

    # Set HOME for modelRoot location (output location) in fre make
    old_home = os.environ["HOME"]
    os.environ["HOME"] = str(Path(OUT_PATH))

    # run checkout
    result = runner.invoke(
        fre.fre, args=["make", "checkout-script", "-y", f"{yamlfile}/null_model.yaml", "-p", platform, "-t", target]
    )

    os.environ["HOME"] = old_home

    # Check for successful command, creation of checkout script, and that script is executable
    # os.access - checks is file has specific access mode, os.X_OK - checks executable permission
    assert all(
        [
            result.exit_code == 0,
            Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh").exists(),
            os.access(Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh"), os.X_OK),
        ]
    )


def test_cli_fre_make_create_checkout_baremetal_npc():
    """fre make checkout -y null_model.yaml -p ncrc5.intel23 -t debug -npc"""

    OUT_PATH = f"{OUT_PATH_BASE}/fremake_out_baremetal_npc"

    # Set paths and click options
    yamlfile = Path("fre/make/tests/null_example/")
    platform = "ncrc5.intel23"
    target = "debug"

    # Delete existing checkout.sh if it exists
    if Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh").exists():
        Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh").unlink()

    # Create output path to test that files exist
    Path(OUT_PATH).mkdir(parents=True, exist_ok=True)

    # Set HOME for modelRoot location (output location) in fre make
    old_home = os.environ["HOME"]
    os.environ["HOME"] = str(Path(OUT_PATH))

    # run checkout
    result = runner.invoke(
        fre.fre,
        args=["make", "checkout-script", "-y", f"{yamlfile}/null_model.yaml", "-p", platform, "-t", target, "-npc"],
    )

    os.environ["HOME"] = old_home

    # Check for successful command, creation of checkout script, and that script is executable
    # os.access - checks is file has specific access mode, os.X_OK - checks executable permission
    assert all(
        [
            result.exit_code == 0,
            Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh").exists(),
            os.access(Path(f"{OUT_PATH}/fremake_canopy/test/null_model_full/src/checkout.sh"), os.X_OK),
        ]
    )


def test_cli_fre_make_create_checkout_container():
    """fre make checkout -y null_model.yaml -p hpcme.2023 -t debug"""

    OUT_PATH = f"{OUT_PATH_BASE}/fremake_out_container"

    # Set paths and click options
    yamlfile = Path("fre/make/tests/null_example/")
    platform = "hpcme.2023"
    target = "debug"

    # Delete existing checkout.sh if it exists
    if Path(f"tmp/{platform}/checkout.sh").exists():
        Path(f"tmp/{platform}/checkout.sh").unlink()

    # Create output path to test that files exist
    Path(OUT_PATH).mkdir(parents=True, exist_ok=True)

    # Set HOME for modelRoot location (output location) in fre make
    old_home = os.environ["HOME"]
    os.environ["HOME"] = str(Path(OUT_PATH))

    # run checkout
    result = runner.invoke(
        fre.fre, args=["make", "checkout-script", "-y", f"{yamlfile}/null_model.yaml", "-p", platform, "-t", target]
    )

    os.environ["HOME"] = old_home

    # Check for successful command, creation of checkout script, and that script is executable
    # os.access - checks is file has specific access mode, os.X_OK - checks executable permission
    assert all(
        [
            result.exit_code == 0,
            Path(f"tmp/{platform}/checkout.sh").exists(),
            not os.access(Path(f"tmp/{platform}/checkout.sh"), os.X_OK),
        ]
    )


def test_cli_fre_make_create_checkout_cleanup():
    """make sure the checked out code doesnt stick around to mess up another pytest call"""
    assert Path(OUT_PATH_BASE).exists()
    shutil.rmtree(OUT_PATH_BASE)
    assert not Path(OUT_PATH_BASE).exists()
