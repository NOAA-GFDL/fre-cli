import numpy as np
from pathlib import Path
import shutil
import yaml
import xarray as xr

N = 20
Np = N + 1
ntiles = 6
ncomponents = 3
skip_component = -99
date = "20250729"

yamlfile = "test_yaml.yaml"
grid_spec = "grid_spec.nc"
input_grid = f"C{N}"
input_dir = "test_inputs"
inputRealm = "atmos"
input_mosaic = f"{input_grid}_mosaic.nc"
input_files = ["atmos_daily_cmip", "atmos_diurnal"]

def cleanup():

  if Path(yamlfile).exists():
    Path(yamlfile).unlink()

  if Path(grid_spec).exists():
    Path(grid_spec).unlink()

  if Path(input_mosaic).exists():
    Path(input_mosaic).unlink()

  if Path(input_dir).exists():
    shutil.rmtree(input_dir)


def set_test(N_in: int = None,
             ntiles_in: int = None,
             date_in: str = None,
             yamlfile_in: str = None,
             grid_spec_in: str = None,
             ncomponents_in: int = None,
             skip_component_in: int = None,
             inputRealm_in: str = None,
             input_mosaic_in: str = None,
             input_grid_in: str = None,
             input_dir_in: str = None,
             input_files_in: list[str] = None):

  global Np, N, ntiles, grid_spec, input_grid, input_files
  global ncomponents, date, input_mosaic, source_gridtype
  global skip_component, input_dir, yamlfile

  if N_in is not None: N, Np = N_in, N_in+1
  if ntiles_in is not None: ntiles = ntiles_in
  if date_in is not None: date = date_in
  if ncomponents_in is not None: ncomponents = ncomponents_in
  if skip_component_in is not None: skip_component = skip_component_in
  if yamlfile_in is not None: yamlfile = yamlfile_in
  if grid_spec_in is not None: grid_spec = grid_spec_in
  if input_grid_in is not None: input_grid = input_grid_in
  if input_mosaic_in is not None: input_mosaic = input_mosaic_in
  if inputRealm_in is not None: inputRealm = inputRealm_in
  if input_files_in is not None: input_files = input_files
  if input_dir_in is not None: input_dir = input_dir_in


def make_yaml():

  ppyaml = {}
  ppyaml["name"] = "regrid_xy_test"

  directories = ppyaml["directories"] = {}
  directories["history_dir"] = "./"
  directories["pp_dir"] = "./"

  postprocess = ppyaml["postprocess"] = {}

  postprocess["settings"] = {"pp_grid_spec": grid_spec}

  components = postprocess["components"] = []
  for i in range(1,ncomponents+1):

    component = {"xyInterp": f"{N},{N}",
                 "interpMethod": "conserve_order2",
                 "inputRealm": f"{inputRealm}",
                 "type": f"faketype{i}",
                 "sources": [{"history_file": f"{ifile}{i}"} for ifile in input_files],
                 "postprocess_on": True}

    if i == skip_component: component["postprocess_on"] = False
    components.append(component)

  with open(yamlfile, "w") as openedfile:
    yaml.dump(ppyaml, openedfile, sort_keys=False)


def make_grid_spec():
  xr.Dataset(data_vars={"atm_mosaic_file": f"{input_mosaic}".encode(),
                        "lnd_moasic_file": f"{input_mosaic}".encode(),
                        "ocn_mosaic_file": "ocean_mosaic.nc".encode()}
             ).to_netcdf(grid_spec)


def make_mosaic():

  if ntiles > 1:
    gridfiles = [f"{input_grid}.tile{i}.nc".encode() for i in range(1,ntiles+1)]
    gridtiles = [f"tile{i}".encode() for i in range(1,ntiles+1)]
  else:
    gridfiles = f"{input_grid}.nc".encode()
    gridtiles = f"tile1".encode()

  data = dict(gridfiles =  xr.DataArray(gridfiles, dims=["ntiles"]).astype("|S255"),
              gridtiles = xr.DataArray(gridtiles, dims=["ntiles"]).astype("|S255")
  )

  xr.Dataset(data_vars=data).to_netcdf(f"{input_dir}/{input_mosaic}")


def make_grid():

  xy = np.arange(0, Np, 1, dtype=np.float64)
  area = np.ones((N, N), dtype=np.float64)

  x, y = np.meshgrid(xy, xy)

  data = dict(x = xr.DataArray(x, dims=["nyp", "nxp"]),
              y = xr.DataArray(y, dims=["nyp", "nxp"]),
              area = xr.DataArray(area, dims=["ny", "nx"])
  )

  for i in range(1, ntiles+1):
    data["tile"] = xr.DataArray(f"tile{i}".encode()).astype("|S255")
    xr.Dataset(data).to_netcdf(f"{input_dir}/{input_grid}.tile{i}.nc")


def make_data():

  data = {}
  data["mister"] = xr.DataArray(np.full((N,N), 1.0, dtype=np.float64), dims=["ny", "nx"])
  data["darcy"] = xr.DataArray(np.full((N,N), 2.0, dtype=np.float64), dims=["ny", "nx"])
  data["wet_c"] = xr.DataArray(np.full((N,N), 5.0, dtype=np.float64), dims=["ny", "nx"])

  coords = {"nx": np.arange(1,Np, dtype=np.float64),
            "ny": np.arange(1,Np, dtype=np.float64)}

  dataset = xr.Dataset(data_vars=data, coords=coords)

  for ifile in input_files:
    for icomponent in range(1,ncomponents+1):
      for i in range(1, ntiles+1): dataset.to_netcdf(f"{input_dir}/{date}.{ifile}{icomponent}.tile{i}.nc")


def make_all():
  make_yaml()
  make_grid_spec()
  make_mosaic()
  make_grid()
  make_data()
