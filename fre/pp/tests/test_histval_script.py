"""
Test nccheck_script
"""
from pathlib import Path
from fre.pp import histval_script as histval
import subprocess

# Set example input paths

test_dir = Path("fre/tests/test_files/ascii_files")
ncgen_input1 = Path(f"{test_dir}/00010101.atmos_month.tile1.cdl")
ncgen_input2 = Path(f"{test_dir}/00010101.atmos_month.tile2.cdl")
ncgen_input3 = Path(f"{test_dir}/00010101.ocean_cobalt_btm.cdl")
ncgen_input4 = Path(f"{test_dir}/00010101.ocean_cobalt_fdet_100.cdl")

input_paths = [ncgen_input1, ncgen_input2, ncgen_input3, ncgen_input4]

ncgen_output1 = Path("./00010101.atmos_month.tile1.nc")
ncgen_output2 = Path("./00010101.atmos_month.tile2.nc")
ncgen_output3 = Path("./00010101.ocean_cobalt_btm.cdl")
ncgen_output4 = Path("./00010101.ocean_cobalt_fdet_100.cdl")

output_paths = [ncgen_output1, ncgen_output2, ncgen_output3, ncgen_output4]

def test_setup_histval(capfd):

    for _path1 in output_paths:
        if Path(_path1).exists():
            Path(_path1).unlink()

    for _path2 in input_paths:
        assert Path(_path2).exists()

    for num in enumerate(input_paths):
        ex = ["ncgen3", "-k", "netCDF-4", "-o", f"ncgen_output{num}", f"ncgen_input{num}" ]

        sp = subprocess.run(ex, check = True)

        assert all( [ sp.returncode == 0, Path(f"ncgen_output{num}").exists() ] )
    _out, _err = capfd.readouterr()

def test_histval(capfd):
    """
    Test the functionality of the histval tool
    """

    result=(histval.validate(test_dir,'00010101',warn=None))

    for x in output_paths:
        Path(x).unlink()

    assert result == 1
    _out, _err = capfd.readouterr()
