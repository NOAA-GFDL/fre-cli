import logging
import os
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
  If the input mosaic file is not in input_dir, this function will copy the input mosaic file to input_dir.
  
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  :raises IOError: Error if the input mosaic file cannot be found in the current or input directory

  .. note:: The input mosaic filename is a required input argument for fregrid.
            The input mosaic contains the input grid information.
  """
  
  input_dir = datadict["input_dir"]
  grid_spec = datadict["grid_spec"]
  
  match datadict["component"]["inputRealm"]:
    case "atmos": mosaic_key = "atm_mosaic_file"
    case "ocean": mosaic_key = "ocn_mosaic_file"
    case "land": mosaic_key = "lnd_mosaic_file"    
  
  mosaic_file = str(xr.load_dataset(grid_spec)[mosaic_key].values.astype(str))
  
  if Path(f"{input_dir}/{mosaic_file}").exists():
    pass
  elif Path(mosaic_file).exists():
    shutil.copy(mosaic_file, f"{input_dir}/{mosaic_file}")
    fre_logger.info(f"Copying {mosaic_file} to input directory {input_dir}") 
  else:
    raise IOError(f"Cannot find input mosaic file {mosaic_file} in current or input directory {input_dir}")

  return mosaic_file


def get_grid_spec(datadict: dict) -> str:
  
  """
  Gets the grid_spec.nc file from the tar file specified in 
  yaml["postprocess"]["settings"]["pp_grid_spec"]
  
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  
  :raises IOError:  Error if grid_spec.nc file cannot be found in the tar file
  
  .. note:: All grid_spec files are expected to be named "grid_spec.nc".  
            The grid_spec file is required in order to obtain the 
            input mosaic filename 
  """
  
  grid_spec = "grid_spec.nc"
  
  pp_grid_spec_tar = datadict["yaml"]["postprocess"]["settings"]["pp_grid_spec"]
  
  #untar grid_spec tar file
  if tarfile.is_tarfile(pp_grid_spec_tar):
    with tarfile.open(pp_grid_spec_tar, 'r') as tar: tar.extractall() 
    
  if not Path(grid_spec).exists():
    raise IOError(f"Cannot find {grid_spec} in tar file {pp_grid_spec_tar}")
  
  return grid_spec
    

def get_input_file(datadict: dict, history_file: str) -> str: 
  
  """
  Formats the input file name where the input file contains the variable data that will be regridded.

  :datadict: dictionary containing relevant regrid parameters
  :type datadict:dict 
  :history_file: history file type 
  :type history_file: str

  .. note:: The input filenames are required arguments for fregrid and refer to the history files containing the 
  data that will be regridded.  A time series of history files exist for regridding:.e.g., 
  20250805.atmos_daily_cmip.tile1.nc, 20250805.atmos_daily_cmip.tile2.nc, ..., 20250805.atmos_daily_cmip.tile6.nc, 
  The yaml configuration does not contain the exact history filenames and the filenames need to be constructed by
  (1) extracting the history file "type" from the yaml configuration.  This type corresponds to the field value of
  yaml["postprocess"]["components"]["sources"]["history_file"] and for example, be "atmos_daily_cmip"  
  (2) prepending YYYYMMDD to the filename.  This function will prepend the date if the date string was passed to the
  entrypoint function regrid_xy of this module:  i.e., this function will return "20250805.atmos_daily_cmip"
  (3) Fregrid will append the tile numbers ("tile1.nc") for reading in the data
  """
  
  input_date = datadict["input_date"]
  return history_file if input_date is None else f"{input_date}.{history_file}"
  
  
def get_remap_file(datadict: dict):

  """
  Determines the remap filename based on the input mosaic filename, output grid size, and 
  conservative order.  For example, this function will return the name
  C96_mosaicX180x288_conserve_order1.nc where the input mosaic filename is C96_mosaic.nc and 
  the output grid size has 180 longitudional cells and 288 latitudonal cells.  

  This function will also copy the remap file to the input directory if the remap file had
  been generated and saved in the output directory from remapping previous components
  
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  
  ..note:: remap_file is a required fregrid argument.  If the remap_file exists, then 
           fregrid will read in the remapping parameters (the exchange grid for conservative methods) 
           from the remap_file for regridding the variables.  If the remap_file does not exist, 
           fregrid will compute the remapping parameters and save them to the remap_file
  """
    
  input_dir = datadict["input_dir"]
  output_dir = datadict["output_dir"]
  input_mosaic = datadict["input_mosaic"]
  nlon = datadict["output_nlon"]
  nlat = datadict["output_nlat"]
  interp_method = datadict["interp_method"]  
  
  remap_file = f"{input_mosaic[:-3]}X{nlon}by{nlat}_{interp_method}.nc"
  
  if not Path(f"{input_dir}/{remap_file}").exists():
    if Path(f"{output_dir}/{remap_file}").exists():
      shutil.copy(f"{output_dir}/{remap_file}", f"{input_dir}/{remap_file}")
      fre_logger.info(f"Remap file {remap_file} in {output_dir} copied to input directory {input_dir}")
    else:
      fre_logger.info(f"Cannot find specified remap_file {remap_file}\n"
                      "Remap file {remap_file} will be generated and saved to the output directory"
                      f"{output_dir}")

  return remap_file


def get_scalar_fields(datadict: dict) -> str:

  """
  Returns the scalar_fields argument for fregrid.
  Scalar_fields is a string of comma separated list of variables
  that will be regridded

  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict

  ..note:: With the exception of the variables in the list
           non_regriddable_variables, all variables
           will be regridded.
  """
  
  mosaic_file = f"{datadict['input_dir']}/{datadict['input_mosaic']}"
  input_file = f"{datadict['input_dir']}/{datadict['input_file']}"
  
  input_file += ".tile1.nc" if xr.load_dataset(mosaic_file).sizes["ntiles"] > 1 else ".nc"
  
  #xarray gives an error if variables in non_regriddable_variables do not exist in the dataset
  #The errors="ignore" overrides the error
  dataset = xr.load_dataset(str(input_file)).drop_vars(non_regriddable_variables, errors="ignore")
  
  return ",".join([variable for variable in dataset if len(dataset[variable].sizes)>1])


def write_summary(datadict):

  """
  Logs a summary of the component that will be regridded in a human-readable format

  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  """
  
  fre_logger.info("COMPONENT SUMMARY")
  fre_logger.info(f"FREGRID input directory: {datadict['input_dir']}")
  fre_logger.info(f"FREGRID output_directory: {datadict['output_dir']}")
  fre_logger.info(f"FREGRID input mosaic file: {datadict['input_mosaic']}")
  fre_logger.info(f"FREGRID input_file: {datadict['input_file']}")
  fre_logger.info(f"FREGRID remap_file: {datadict['remap_file']}")
  fre_logger.info(f"FREGRID output lonxlat grid: {datadict['output_nlon']} X {datadict['output_nlat']}")
  fre_logger.info(f"FREGRID interp method: {datadict['interp_method']}")
  fre_logger.info(f"FREGRID scalar_fields: {datadict['scalar_field']}")
  
  
def regrid_xy(yamlfile: str,
              input_dir: str,
              output_dir: str,
              components: list[str] = None,
              input_date: str = None):
    
  """
  Submits a fregrid job for each regriddable component in the model yaml file.

  :yamlfile: yaml file containing specifications for yaml["postprocess"]["settings"]["pp_grid_spec"]
             and yaml["postprocess"]["components"]

  :Input_dir: Name of the input directory containing the input mosaic file, remap file, 
              and input/history files.  Fregrid will look for all input files in input_dir. 
  :Output_dir: Name of the output directory where fregrid outputs will be saved
  :Components: List of component 'types' to regrid, e.g., components = ['aerosol', 'atmos_diurnal, 'land']
               If components is not specified, all components in the yaml file with postprocess_on = true 
               will be remapped
  :Input_date: Datestring in the format of YYYYMMDD that corresponds to the date prefix of the history files, 
               e.g., input_date=20250730 where the history filename is 20250730.atmos_month_aer.tile1.nc
  """
  
  datadict = {}
  
  #load yamlfile to thisyaml
  with open(yamlfile, 'r') as openedfile: thisyaml = yaml.safe_load(openedfile)

  #save arguments to datadict
  datadict["yaml"] = thisyaml  
  datadict["grid_spec"] = get_grid_spec(datadict)  
  datadict["input_dir"] = input_dir
  datadict["output_dir"] = output_dir
  datadict["input_date"] = input_date

  datadict["current_dir"] = current_dir = os.getcwd()
  
  #get list of components to regrid
  components_list = thisyaml['postprocess']['components']
  if components is not None: 
    for component in components_list:
      if component["type"] not in components: components_list.remove(component)

  #submit fregrid job for each component
  for component in components_list:        
    
    if component["postprocess_on"] is False:       
      fre_logger.info(f"skipping component {component['type']}")
      continue
    
    datadict["component"] = component    
    datadict["input_mosaic"] = get_input_mosaic(datadict)

    [output_nlat, output_nlon] = [int(dims) for dims in component["xyInterp"].split(",")]
    datadict["output_nlat"] = output_nlat
    datadict["output_nlon"] = output_nlon
                
    datadict["interp_method"] = component["interpMethod"]

    #iterate over each history file in the component
    for history_dict in component["sources"]:

      datadict["input_file"] = get_input_file(datadict, history_dict["history_file"])      
      datadict["output_file"] = datadict["input_file"]          
      datadict["scalar_field"] = get_scalar_fields(datadict)                  
      datadict["remap_file"] = get_remap_file(datadict)
      
      write_summary(datadict)

      fregrid_command = ["fregrid",
                         "--debug",
                         "--standard_dimension",
                         "--input_mosaic", input_dir+'/'+datadict["input_mosaic"],
                         "--input_file", input_dir+'/'+datadict["input_file"],
                         "--interp_method", datadict["interp_method"],
                         "--remap_file", input_dir+'/'+datadict["remap_file"],
                         "--nlon", str(datadict["output_nlon"]),
                         "--nlat", str(datadict["output_nlat"]),
                         "--scalar_field", datadict["scalar_field"],
                         "--output_dir", datadict["output_dir"],
                         "--output_file", datadict["output_file"]
      ]

      fregrid_job = subprocess.run(fregrid_command, capture_output=True, text=True)

      if fregrid_job.returncode == 0:
        fre_logger.info(fregrid_job.stdout.split("\n")[-3:])
      else:
        raise RuntimeError(fregrid_job.stderr)
        
