import numpy as np
from pathlib import Path
import shutil
import tarfile
import yaml
import xarray as xr

nxy = 20
nxyp = nxy + 1
ntiles = 6
date = "20250729"

yamlfile = "test_yaml.yaml"
grid_spec_tar = "grid_spec.tar"
input_grid = f"C{nxy}"
input_dir = "test_inputs"
input_mosaic = f"{input_grid}_mosaic.nc"
components: dict =  None
tar_list: list = None

def cleanup():

  if Path(yamlfile).exists():
    Path(yamlfile).unlink()

  if Path("grid_spec.nc").exists():
    Path("grid_spec.nc").unlink()

  if Path(grid_spec_tar).exists():
    Path(grid_spec_tar).unlink()

  if Path(input_mosaic).exists():
    Path(input_mosaic).unlink()

  if Path(input_dir).exists():
    shutil.rmtree(input_dir)

  for i in range(1, ntiles+1):
    gridfile = Path(f"{input_grid}.tile{i}.nc")
    if gridfile.exists(): gridfile.unlink()


def set_test(components_in: dict,
             nxy_in: int = None,
             ntiles_in: int = None,
             date_in: str = None,
             yamlfile_in: str = None,
             grid_spec_tar_in: str = None,
             input_mosaic_in: str = None,
             input_grid_in: str = None,
             input_dir_in: str = None):

  global components
  global nxyp, nxy, ntiles, grid_spec_tar, input_grid
  global date, input_mosaic
  global input_dir, yamlfile
  global tar_list

  components = components_in
  if nxy_in is not None:
    nxy = nxy_in
    nxyp = nxy_in+1
    input_grid = f"C{nxy}"
  if ntiles_in is not None: ntiles = ntiles_in
  if date_in is not None: date = date_in
  if yamlfile_in is not None: yamlfile = yamlfile_in
  if grid_spec_tar_in is not None: grid_spec_tar = grid_spec_tar_in
  if input_grid_in is not None: input_grid = input_grid_in
  if input_mosaic_in is not None: input_mosaic = input_mosaic_in
  if input_dir_in is not None: input_dir = input_dir_in

  tar_list = []

def make_yaml():

  ppyaml = {}
  ppyaml["name"] = yamlfile

  directories = ppyaml["directories"] = {}
  directories["history_dir"] = "./"
  directories["pp_dir"] = "./"

  postprocess = ppyaml["postprocess"] = {}
  postprocess["settings"] = {"pp_grid_spec": grid_spec_tar}
  postprocess["components"] = components

  with open(yamlfile, "w") as openedfile:
    yaml.dump(ppyaml, openedfile, sort_keys=False)


def make_grid_spec():
  xr.Dataset(data_vars={"atm_mosaic_file": f"{input_mosaic}".encode(),
                        "lnd_mosaic_file": f"{input_mosaic}".encode(),
                        "ocn_mosaic_file": "ocean_mosaic.nc".encode()}
             ).to_netcdf("grid_spec.nc")

  tar_list.append("grid_spec.nc")


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

  xr.Dataset(data_vars=data).to_netcdf(f"{input_mosaic}")

  tar_list.append(f"{input_mosaic}")


def make_grid():

  xy = np.arange(0, nxyp, 1, dtype=np.float64)
  area = np.ones((nxy, nxy), dtype=np.float64)

  x, y = np.meshgrid(xy, xy)

  data = dict(x = xr.DataArray(x, dims=["nyp", "nxp"]),
              y = xr.DataArray(y, dims=["nyp", "nxp"]),
              area = xr.DataArray(area, dims=["ny", "nx"])
  )

  for i in range(1, ntiles+1):
    data["tile"] = xr.DataArray(f"tile{i}".encode()).astype("|S255")
    xr.Dataset(data).to_netcdf(f"{input_grid}.tile{i}.nc")

    tar_list.append(f"{input_grid}.tile{i}.nc")


def make_data():

  data = {}
  data["mister"] = xr.DataArray(np.full((nxy,nxy), 1.0, dtype=np.float64), dims=["ny", "nx"])
  data["darcy"] = xr.DataArray(np.full((nxy,nxy), 2.0, dtype=np.float64), dims=["ny", "nx"])
  data["wins"] = xr.DataArray(np.full((nxy,nxy), 3.0, dtype=np.float64), dims=["ny", "nx"])
  data["wet_c"] = xr.DataArray(np.full((nxy,nxy), 5.0, dtype=np.float64), dims=["ny", "nx"])

  coords = {"nx": np.arange(1,nxyp, dtype=np.float64),
            "ny": np.arange(1,nxyp, dtype=np.float64)}

  dataset = xr.Dataset(data_vars=data, coords=coords)

  for component in components:
    for source in component["sources"]:
      history_file = source["history_file"]
      for i in range(1, ntiles+1):
        dataset.to_netcdf(f"{input_dir}/{date}.{history_file}.tile{i}.nc")
    try:
      for static_source in component["static"]:
        history_file = static_source["source"]
        for i in range(1, ntiles+1):
          dataset.to_netcdf(f"{input_dir}/{date}.{history_file}.tile{i}.nc")
    except KeyError:
        pass


def make_all():
  make_yaml()
  make_grid_spec()
  make_mosaic()
  make_grid()
  make_data()

  with tarfile.open(grid_spec_tar, "w") as tar:
    for ifile in tar_list: tar.add(ifile)

  for ifile in tar_list:
    Path(ifile).unlink()
