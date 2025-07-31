import numpy as np
import yaml
import xarray as xr

N = 20
Np = N + 1
ntiles = 6
grid_spec = "grid_spec.nc"
input_grid = f"C{N}"
inputRealm = "atmos"
input_mosaic = f"{input_grid}_mosaic.nc"
input_files = ["atmos_daily_cmip", "atmos_diurnal"]

def set_N(N_in: int = None,
          ntiles_in: int = None,
          grid_spec_in: str = None,
          inputRealm_in: str = None,
          input_grid_in: str = None,
          input_files_in: list[str] = None):
  
  global Np, N, ntiles, grid_spec, input_grid, input_files
  global input_mosaic_in, source_gridtype
  
  if N_in is not None: N, Np = N_in, N_in+1      
  if ntiles_in is not None: ntiles = ntiles_in
  if grid_spec_in is not None: grid_spec = grid_spec_in
  if input_grid_in is not None: input_grid = input_grid_in
  if input_mosaic_in is not None: input_mosaic = input_mosaic_in
  if inputRealm_in is not None: inputRealm = inputRealm_in
  if input_files_in is not None: input_files = input_files
  

def make_pp_yaml(yamlfile: str = "test_pp.yaml"):

  ppyaml = {}
  ppyaml["name"] = "regrid_xy_test"
    
  directories = ppyaml["directories"] = {}
  directories["history_dir"] = "./"
  directories["pp_dir"] = "./"

  postprocess = ppyaml["postprocess"] = {}
  
  postprocess["settings"] = {"pp_grid_spec": grid_spec}
  
  components = postprocess["components"] = []
  for i in range(5):

    component = {"xyInterp": f"{N},{N}",
                 "interpMethod": "conserve_order2", 
                 "inputRealm": f"{inputRealm}", 
                 "sources": [{"history_file": ifile} for ifile in input_files],
                 "postprocess_on": True}
    if i == 2: component["postprocess_on"] = False
    components.append(component)
  
  with open(yamlfile, "w") as openedfile:
    yaml.dump(ppyaml, openedfile, sort_keys=False)
  

def make_grid_spec():
  xr.Dataset(data_vars={"atm_mosaic_file": f"{input_mosaic}",
                        "lnd_moasic_file": f"{input_mosaic}",
                        "ocn_mosaic_file": "ocean_mosaic.nc"}
             ).to_netcdf(grid_spec)

 
def make_mosaic():
  
  if ntiles > 1:
    gridfiles = [f"{input_grid}.tile{i}.nc" for i in range(1,ntiles+1)]
  else:
    gridfiles = f"{input_grid}.nc"
  
  gridfiles = xr.DataArray(gridfiles, dims=["ntiles"])
    
  xr.Dataset(data_vars={"gridfiles": gridfiles}).to_netcdf(input_mosaic)
  
    
def make_grid():
  
  xy = np.arange(0, Np+1, 1, dtype=np.float64)
  area = np.ones((N, N), dtype=np.float64)
  
  x, y = np.meshgrid(xy, xy)
  
  x = xr.DataArray(x, dims=["nyp", "nxp"])
  y = xr.DataArray(y, dims=["nyp", "nxp"])
  area = xr.DataArray(area, dims=["ny", "nx"])
  
  dataset = xr.Dataset(data_vars={'x': x, 'y': y, "area": area})
  
  for i in range(1, ntiles+1): dataset.to_netcdf(f"{input_grid}.tile{i}.nc")

  
def make_data(date: str):
  
  mister = xr.DataArray(np.full((N,N), 1.0, dtype=np.float64), dims=["ny", "nx"])
  darcy = xr.DataArray(np.full((N,N), 2.0, dtype=np.float64), dims=["ny", "nx"])
  wet_c = xr.DataArray(np.full((N,N), 5.0, dtype=np.float64), dims=["ny", "nx"])
  
  dataset = xr.Dataset(data_vars={"mister": mister, "darcy": darcy, "wet_c": wet_c})
  
  for ifile in input_files:
    for i in range(1, ntiles+1): dataset.to_netcdf(f"{date}.{ifile}.tile{i}.nc")

make_pp_yaml()
make_grid_spec()
make_grid()
make_data("20250729")
                   