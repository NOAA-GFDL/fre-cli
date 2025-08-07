import numpy as np
import os
import xarray as xr

import fre.app.regrid_xy.regrid_xy as regrid_xy
import generate_files

def test_regrid_xy():
  
  date = "20250729"
  ncomponents = 5
  skip_component = 3
  input_files = ["atmos_daily_cmip", "atmos_diurnal"]
  input_dir = "test_inputs"
  output_dir = "test_outputs"

  os.makedirs(input_dir, exist_ok=True)
  os.makedirs(output_dir, exist_ok=True)
  
  #generate test files
  generate_files.set_test(date_in=date, input_files_in=input_files, ncomponents_in=ncomponents, input_dir_in=input_dir)
  generate_files.make_all()
  
  regrid_xy.regrid_xy(yamlfile="test_pp.yaml",
                      input_dir=input_dir,
                      output_dir=output_dir,
                      input_date=date)

  #check answers, for the third component, postprocess_on = False
  checkfiles = [f"{output_dir}/{date}.{ifile}{i}.nc" for ifile in input_files
                for i in range(1,ncomponents+1) if i!=skip_component]
  for outfile in checkfiles:

    checkme = xr.load_dataset(outfile)
  
    assert "wet_c" not in checkme
    assert "mister" in checkme
    assert "darcy" in checkme
    
    assert np.all(checkme["mister"].values==np.float64(1.0))
    assert np.all(checkme["darcy"].values==np.float64(2.0))
    
    
if __name__ == "__main__":
  test_regrid_xy()
  
  
