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
  Gets the input mosaic filename from the grid_spec file
  
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  :raises IOError if the input mosaic file cannot be found in the current directory or the input directory
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
    fre_logger(f"Input mosaic file {input_dir}{mosaic_file} exists")
  elif Path(mosaic_file).exists():
    shutil.copy(mosaic_file, input_dir+mosaic_file)
    fre_logger(f"Copying {mosaic_file} to input directory {input_dir}") 
  else:
    raise IOError(f"Input mosaic file {mosaic_file} could not be found")
  
  return mosaic_file
      

def get_grid_spec(grid_spec: str, datadict: dict) -> str:
  
  """
  Gets the grid_spec file by first extracing the tar file,
  where the tar file is the value of thisyaml["postprocess"]["settings"]["pp_grid_spec"]
  in the thisyaml file.
  
  :grid_spec:  User-specified grid_spec filename.  
               If not specified, grid_spec will be set to 'grid_spec.nc'
  :type grid_spec: str
  :datadict: dictionary containing relevant regrid parameters
  :type datadict: dict
  
  :raises IOError:  Error if the grid_spec file cannot be found
  """
  
  grid_spec = "grid_spec.nc"
    
  #retrieve the grid_spec tar filename from yaml
  pp_grid_spec_tar = datadict["yaml"]['postprocess']['settings']['pp_grid_spec']
    
  #untar grid_spec tar file
  if tarfile.is_tarfile(pp_grid_spec_tar):
    with tarfile.open(pp_grid_spec_tar, 'r') as tar: tar.extractall() 
        
  if Path(grid_spec).exists():
    fre_logger(f"Grid_spec file {grid_spec} found in {pp_grid_spec_tar}")
    return grid_spec
  else:
    raise IOError(f"Grid_spec={grid_spec} could not be found in {pp_grid_spec_tar}")
    

def get_input_file(datadict: dict, history_file: str):
  
  """
  Gets the 
  """
  
  input_date = datadict["input_date"]
  if input_date is None:
    return history_file
  else:
    return f"{input_date}.{history_file}"


def get_remap_file(datadict: dict):

  input_dir = datadict["input_dir"]
  input_mosaic = datadict["input_mosaic"]
  nlon = datadict["output_nlon"]
  nlat = datadict["output_nlat"]
  interp_method = datadict["interp_method"]  
    
  remap_file = f"{input_mosaic[:-3]}X{nlon}by{nlat}_{interp_method}.nc"

  if Path(f"{inpu_dir}{remap_file}").exists():
    fre_logger.info(f"Remap file {remap_file} found in {input_dir}")
  else if Path(remap_file).exists():
    shutil.copy(remap_file, input_dir+remap_file)
    fre_logger.info(f"Remap file {remap_file} found in {input_dir}")
  else:
    fre_logger.info(f"Cannot find specified remap_file {remap_file}\n"
                    "Remap file {remap_file} will be generated on-the-fly")

  return remap_file


def get_scalar_fields(datadict: dict):

    """
    Returns all the regriddable variables in an input file
    """
    
    mosaic_file = datadict["input_mosaic"]
    input_file = datadict["input_file"]
    
    if xr.load_dataset(str(mosaic_file)).sizes["ntiles"] > 1:
      input_file += ".tile1.nc"
    else:
      input_file += ".nc"
    
    #load data file
    #xarray gives an error if variables to drop do not exist in the file.  The errors="ignore" fixes that
    dataset = xr.load_dataset(str(input_file)).drop_vars(non_regriddable_variables, errors="ignore")

    #list of variables to regrid, only multi-dimensional data will be regridded
    regrid_vars_string = ",".join([variable for variable in dataset if len(dataset[variable].sizes)>1])

    return regrid_vars_string


def write_summary(datadict):
  
  fre_logger("JOB SUMMARY")
  fre_logger(f"FREGRID input directory: {datadict['input_dir']}")
  fre_logger(f"FREGRID output_directory: {datadict['output_dir']}")
  fre_logger(f"FREGRID input mosaic file: {datadict['input_mosaic']}")
  fre_logger(f"FREGRID output lonxlat grid: {datadict['output_nlon']} X {datadict['output_nlat']}")
  fre_logger(f"FREGRID remap file: {datadict['remap_file']}")
  

def regrid_xy(yamlfile: str,
              input_dir: str,
              output_dir: str,
              only_thesecomponents: list[int] = None,
              input_date: str = None,
):
    
  """
  Remaps variables for each component element in the post-processing thisyaml file.
  If regrid_thesecomponents is not specified, regrid_xy will regrid all components.
  To regrid only specific components, regrid_thesecomponents must have the element number
  of the component to regrid.      
  """
    
  datadict = {}
    
  #load thisyaml_file to a dictionary
  with open(yamlfile, 'r') as openedfile: thisyaml = thisyaml.safe_load(openedfile)
  
  datadict["yaml"] = thisyaml
  fre_logger(f"Extracting regrid information from yaml file {yamlfile}")

  #get grid_spec file
  datadict["grid_spec"] = get_grid_spec(datadict)

  #set input and output directory names if not specified 
  datadict["input_dir"] = input_dir + "/"
  datadict["output_dir"] = output_dir + "/"
  datadict["input_date"] = input_date

  #get components to remap 
  if only_thesecomponents is None:
      #regrid all components
      components = thisyaml['postprocess']['components']
  else:
      #regrid only components specified in the list only_thesecomponents
      components = [thisyaml['postprocess']['components'][i] for i in regrid_thesecomponents]

  #iterate over components that will be regridded
  count_component = 0
  for component in components:        

    count_component += 1

    #skip if postprocessing is turned off for the component
    if component['postprocess_on'] is False: 
      
      fre_logger(f"skipping component number ${count_component}")
      continue

    fre_logger(f"determining regrid specifications for component number {count_component}")
    
    datadict["component"] = component

    #get input mosaic filename corresponding to the inputRealm
    datadict["input_mosaic"] = get_input_mosaic(datadict)

    #get output grid dimensions
    [output_nlat, output_nlon] = [int(dims) for dims in component['xyInterp'].split(",")]
    datadict["output_nlat"] = output_nlat
    datadict["output_nlon"] = output_nlon
                
    #get interp_method: bilinear, conserve_interp1, conserve_interp2
    datadict["interp_method"] = component['interpMethod']

    #remap each history file in component.  The history file will be
    #specified as, e.g., "atmos_daily_cmip"
    for history_dict in component['sources']:

      #prepend the date to the history_file so that, e.g.,
      datadict["input_file"] = get_input_file(datadict, history_dict["history_file"])
      
      #output file will have the same prefix as the input file
      datadict["output_file"] = datadict["input_file"]
          
      #get all fields to regrid
      datadict["scalar_field"] = get_scalar_fields(datadict)        
          
      #get remap file and name that will be cached
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
