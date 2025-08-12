import numpy as np
from pathlib import Path
import shutil
import xarray as xr

import fre.app.regrid_xy.regrid_xy as regrid_xy
import fre.app.regrid_xy.tests.generate_files as generate_files


def test_regrid_xy():

  """
  Tests the main function regrid_xy and ensures
  data is regridded correctly
  """

  date = "20250729"
  n_components = 5
  skip_component = 3
  input_files = ["atmos_daily_cmip", "atmos_diurnal"]
  yamlfile = "test_yaml.yaml"
  input_dir = Path("test_inputs")
  output_dir = Path("test_outputs")

  input_dir.mkdir(exist_ok=True)
  output_dir.mkdir(exist_ok=True)

  #generate test files
  generate_files.set_test(date_in=date,
                          yamlfile_in=yamlfile,
                          input_files_in=input_files,
                          n_components_in=n_components,
                          input_dir_in=input_dir,
                          skip_component_in=skip_component)

  generate_files.make_all()

  regrid_xy.regrid_xy(yamlfile=yamlfile,
                      input_dir=input_dir.name,
                      output_dir=output_dir.name,
                      input_date=date)

  #check answers, for the third component, postprocess_on = False
  checkfiles = [output_dir/f"{date}.{ifile}{i}.nc" for ifile in input_files
                for i in range(1,n_components+1) if i!=skip_component]
  for outfile in checkfiles:

    checkme = xr.load_dataset(outfile)

    assert "wet_c" not in checkme
    assert "mister" in checkme
    assert "darcy" in checkme

    assert np.all(checkme["mister"].values==np.float64(1.0))
    assert np.all(checkme["darcy"].values==np.float64(2.0))

  #third component should not have been regridded
  for ifile in input_files:
    assert not (output_dir/f"{date}.{ifile}{skip_component}.nc").exists()

  shutil.rmtree(output_dir)
  generate_files.cleanup()


def test_get_input_mosaic():

  """
  Tests get_input_mosaic correctly copies the mosaic file to the input directory
  """

  input_dir = Path("input_dir")
  grid_spec = Path("grid_spec.nc")
  mosaic_file = Path("ocean_mosaic.nc")

  generate_files.make_grid_spec()
  mosaic_file.touch()
  input_dir.mkdir(exist_ok=True)

  datadict=dict(input_dir=input_dir, grid_spec=grid_spec, component={"inputRealm":"ocean"})

  #copy mosaic_file to input_dir and return mosaic_file/input_dir
  check = regrid_xy.get_input_mosaic(datadict)
  assert check == str(input_dir/mosaic_file)
  assert Path(check).exists()

  mosaic_file.unlink()  #clean up
  grid_spec.unlink()  #clean up
  shutil.rmtree(input_dir)  #clean up


def test_get_input_file_argument():

  """
  Tests get_input_file
  """

  input_date = "20250807"
  history_file = "pemberley"
  datadict = {"input_date": input_date}
  assert regrid_xy.get_input_file_argument(datadict, history_file) == input_date + "." + history_file

  datadict["input_date"] = None
  assert regrid_xy.get_input_file_argument(datadict, history_file) == history_file


def test_get_remap_file():

  """
  Tests get_remap_file
  """

  input_dir = Path("input_dir")
  input_mosaic = "C20_mosaic"
  nlon = 40
  nlat = 10
  interp_method = "conserve_order1"

  datadict = {"input_dir": input_dir.name,
              "input_mosaic": input_mosaic+".nc",
              "output_nlon": nlon,
              "output_nlat": nlat,
              "interp_method": interp_method}

  input_dir.mkdir(exist_ok=True)

  #check remap file from current directory is copied to input directory
  remap_file = Path(f"{input_mosaic}X{nlon}by{nlat}_{interp_method}.nc")
  remap_file.touch()

  check = regrid_xy.get_remap_file(datadict)

  assert check == str(input_dir/remap_file)
  assert Path(check).exists()

  shutil.rmtree(input_dir)

