import logging
from pathlib import Path
import subprocess 
import shutil
import tarfile
import xarray as xr
import yaml

fre_logger = logging.getLogger(__name__)

#list of variables/fields that will not be regridded
non_regriddable_variables = [
  'geolon_c', 'geolat_c', 'geolon_u', 'geolat_u', 'geolon_v', 'geolat_v',
  'FA_X', 'FA_Y', 'FI_X', 'FI_Y', 'IX_TRANS', 'IY_TRANS', 'UI', 'VI', 'UO', 'VO',
  'wet_c', 'wet_v', 'wet_u', 'dxCu', 'dyCu', 'dxCv', 'dyCv', 'Coriolis',
  'areacello_cu', 'areacello_cv', 'areacello_bu', 'average_T1','average_T2',
  'average_DT','time_bnds']


def get_input_mosaic(datadict: dict) -> str:
  
  """
  Gets the input mosaic filename from the grid_spec file.  
  If the input mosaic file is not in input_dir, this function will copy the file to input_dir.
  
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  :raises IOError: Error if the input mosaic file cannot be found in the current or input directory

  .. note:: The input mosaic file contains the input grid information for fregrid.
  """
  
  input_dir = datadict["input_dir"]
  grid_spec = datadict["grid_spec"]
  input_realm = datadict["component"]["inputRealm"]
  
  match input_realm:
  case "atmos": mosaic_key = "atm_mosaic_file"
  case "ocean": mosaic_key = "ocn_mosaic_file"
  case "land": mosaic_key = "lnd_mosaic_file"    
  
  mosaic_file = str(xr.load_dataset(grid_spec)[mosaic_key].values.astype(str))
  
  if Path(input_dir+mosaic_file).exists():
    pass
  elif Path(mosaic_file).exists():
    shutil.copy(mosaic_file, input_dir+mosaic_file)
    fre_logger(f"Copying {mosaic_file} to input directory {input_dir}") 
  else:
    raise IOError(f"Input mosaic file {mosaic_file} could not be found")

  return mosaic_file


def get_grid_spec(datadict: dict) -> str:
  
  """
  Ensures the grid_spec.nc file exists.  The grid_spec.nc file
  contains the input mosaic filename that is needed for fregrid.

  The grid_spec file is assumed to be named 'grid_spec.nc' and is extracted 
  from the tarfile corresponding to yaml["postprocess"]["settings"]["pp_grid_spec"]
  
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  
  :raises IOError:  Error if the grid_spec file cannot be found
  """
  
  grid_spec = "grid_spec.nc"
  
  pp_grid_spec_tar = datadict["yaml"]['postprocess']['settings']['pp_grid_spec']
  
  #untar grid_spec tar file
  if tarfile.is_tarfile(pp_grid_spec_tar):
    with tarfile.open(pp_grid_spec_tar, 'r') as tar: tar.extractall() 
    
  if not Path(grid_spec).exists():
    raise IOError(f"Grid_spec file {grid_spec} could not be found in {pp_grid_spec_tar}")

  return grid_spec
    

def get_input_file(datadict: dict, history_file: str):
  
  """
  Gets the 
  """
  
  input_date = datadict["input_date"]
  return history_file if input_date is None else f"{input_date}.{history_file}"
  
  
def get_remap_file(datadict: dict):
    
  input_dir = datadict["input_dir"]
  output_dir = datadict["output_dir"]
  input_mosaic = datadict["input_mosaic"]
  nlon = datadict["output_nlon"]
  nlat = datadict["output_nlat"]
  interp_method = datadict["interp_method"]  
  
  remap_file = f"{input_mosaic[:-3]}X{nlon}by{nlat}_{interp_method}.nc"
  
  if not Path(f"{input_dir}{remap_file}").exists():
    if Path(output_dir+remap_file).exists():
      shutil.copy(remap_file, output_dir+remap_file)
      fre_logger.info(f"Remap file {remap_file} in {output_dir} copied to input directory {input_dir}")
    else:
      fre_logger.info(f"Cannot find specified remap_file {remap_file}\n"
                      "Remap file {remap_file} will be generated on-the-fly")

  return remap_file


def get_scalar_fields(datadict: dict):

  """
  Returns all the regriddable variables in an input file
  """
  
  mosaic_file = str(datadict["input_mosaic"])
  input_file = datadict["input_file"]
  
  input_file += ".tile1.nc" if xr.load_dataset(mosaic_file).sizes["ntiles"] > 1 else ".nc"
  
  #xarray gives an error if variables to drop do not exist in the file.  The errors="ignore" fixes that
  dataset = xr.load_dataset(str(input_file)).drop_vars(non_regriddable_variables, errors="ignore")
  
  return ",".join([variable for variable in dataset if len(dataset[variable].sizes)>1])


def write_summary(datadict):
  
  fre_logger("JOB SUMMARY")
  fre_logger(f"bunch of stff")
  fre_logger(f"FREGRID input directory: {datadict['input_dir']}")
  fre_logger(f"FREGRID output_directory: {datadict['output_dir']}")
  fre_logger(f"FREGRID input mosaic file: {datadict['input_mosaic']}")
  fre_logger(f"FREGRID output lonxlat grid: {datadict['output_nlon']} X {datadict['output_nlat']}")
  fre_logger(f"FREGRID remap file: {datadict['remap_file']}")
  
  
def regrid_xy(yamlfile: str,
              input_dir: str,
              output_dir: str,
              components: list[str] = None,
              input_date: str = None):
    
  """
  Remaps variables for each component element in the yaml file.

  :Input_dir: Name of the input directory containing the input mosaic file, remap file, and history files
              Fregrid will look for all input files in input_dir. 
  :Output_dir: Name of the output directory where fregrid outputs will be saved
  :Components:  List of component 'types' to regrid, e.g., components = ['aerosol', 'atmos_diurnal, 'land']
                If components is not specified, all components with postprocess_on = true will be remapped
  :Input_date: Date prefix in the history file, e.g., input_date=20250730 where the history file name is 
               20250730.atmos_month_aer.tile1.nc
  """
  
  datadict = {}
  
  #load yamlfile to thisyaml
  with open(yamlfile, 'r') as openedfile: thisyaml = thisyaml.safe_load(openedfile)
  
  datadict["yaml"] = thisyaml  
  datadict["grid_spec"] = get_grid_spec(datadict)  
  datadict["input_dir"] = input_dir + "/"
  datadict["output_dir"] = output_dir + "/"
  datadict["input_date"] = input_date

  components_list = thisyaml['postprocess']['components']
  if components is not None:    
    for component in components_list:
      if component["type"] is not in components: components_list.remove(component)
    
  for component in components_list:        
    
    if component['postprocess_on'] is False:       
      fre_logger(f"skipping component {component['type']}")
      continue
    
    datadict["component"] = component    
    datadict["input_mosaic"] = get_input_mosaic(datadict)

    [output_nlat, output_nlon] = [int(dims) for dims in component['xyInterp'].split(",")]
    datadict["output_nlat"] = output_nlat
    datadict["output_nlon"] = output_nlon
                
    datadict["interp_method"] = component['interpMethod']

    for history_dict in component['sources']:

      datadict["input_file"] = get_input_file(datadict, history_dict["history_file"])      
      datadict["output_file"] = datadict["input_file"]          
      datadict["scalar_field"] = get_scalar_fields(datadict)                  
      datadict["remap_file"] = get_remap_file(datadict)
      
      write_summary(datadict)
                        
      fregrid_command = ['fregrid',
                        '--debug',
                        '--standard_dimension',
                        '--input_mosaic', datadict["input_mosaic"],
                        '--input_dir', datadict["input_dir"],
                        '--input_file', datadict["input_file"],
                        '--associated_file_dir', datadict["input_dir"],
                        '--interp_method', datadict["interp_method"],
                        '--remap_file', datadict["remap_file"],
                        '--nlon', datadict["output_nlon"],
                        '--nlat', datadict["output_nlat"],
                        '--scalar_field', datadict["scalar_field"],
                        '--output_dir', datadict["output_dir"],
                        '--output_file', datadict["output_file"]
      ]
      
      print(fregrid_command)
                               
      #fregrid_proc = subprocess.run(fregrid_command, check=True)
