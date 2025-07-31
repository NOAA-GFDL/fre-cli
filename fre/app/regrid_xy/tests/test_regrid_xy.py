import pytest

import fre.app.regrid_xy.regrid_xy_rewrite as regrid_xy
import generate_files

def test_regrid_xy():
  
  date = "20250729"
  
  #generate files
  generate_files.make_pp_yaml()
  generate_files.make_grid_spec()
  generate_files.make_mosaic()
  generate_files.make_grid()
  generate_files.make_data(date)
  
  regrid_xy.regrid_xy(pp_yamlfile="test_pp.yaml",
                      input_date=date)

if __name__ == "__main__":
  test_regrid_xy()
  
  