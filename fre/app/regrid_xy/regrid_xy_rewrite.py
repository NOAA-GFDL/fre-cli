from pathlib import Path
import subprocess 
import tarfile
import xarray as xr
import yaml

#dictionary that maps inputRealm from the pp_yaml the variable name
#holding the mosaic filenames in the grid_spec file
#For example, in grid_spec.nc, atm_mosaic_file = C96_mosaic.nc
#For land, lnd_mosaic_file = C96_mosaic.nc
#For ocn, ocn_mosaic_file = "ocean_mosaic.nc"
map_mosaicfile = dict(atmos = 'atm_mosaic_file',
                      aerosol = 'atm_mosaic_file',
                      ocean = 'ocn_mosaic_file',
                      land = 'lnd_mosaic_file')

#list of variables/fields that will not be regridded
non_regriddable_variables = [
    'geolon_c', 'geolat_c', 'geolon_u', 'geolat_u', 'geolon_v', 'geolat_v',
    'FA_X', 'FA_Y', 'FI_X', 'FI_Y', 'IX_TRANS', 'IY_TRANS', 'UI', 'VI', 'UO', 'VO',
    'wet_c', 'wet_v', 'wet_u', 'dxCu', 'dyCu', 'dxCv', 'dyCv', 'Coriolis',
    'areacello_cu', 'areacello_cv', 'areacello_bu', 'average_T1','average_T2',
    'average_DT','time_bnds']

def get_input_file(input_file: str = None, 
                   input_date: str = ''):

    """
    Intakes the prefix of the input_file returns the filename
    pretended with the input_date so that the filename is YYYYMMDD.input_file.  
    For a cubed sphere, fregrid will append the tile number to the filename 
    such that fregrid will regrid the variables in YYYYMMDD.input_file.tile#.nc
    """
    
    #FRE-NCTools expects input files without the .nc extension
    if ".nc" in input_file: input_file = input_file[:-3]

    return f"{input_date}.{input_file}"


def get_input_mosaic(grid_spec: str, 
                     input_realm: str):

    """
    Intakes the input_realm field from the pp yaml and returns
    the variable in the grid_spec file that contains the mosaic file information
    """
    
    mosaic_key = map_mosaicfile[input_realm]
    return str(xr.load_dataset(grid_spec)[mosaic_key].values.astype(str))
  

def is_tiled(mosaic_file: str):
  
  if xr.load_dataset(str(mosaic_file)).sizes["ntiles"] > 1: return True
  return False


def get_remap_file(remap_file: str, 
                   input_mosaic: str, 
                   output_nlat: int, 
                   output_nlon: int,
                   interp_method: str):

    remap_cache_file = f"{input_mosaic}Xnlon{output_nlon}nlat{output_nlat}_{interp_method}.nc"
    if remap_file is not None:
        try:
          shutil.copy(remap_file, remap_cache_file)
          fre_logger.info(f"Copied {remap_file} to {remap_cache_file}")
        except Exception as exc:
            fre_logger.info(f"Cannot find specified remap_file {remap_file}\n"
                            "Remap file {remap_cache_file} will be generated on-the-fly")

    return remap_cache_file


def get_scalar_fields(input_file: str, is_tiled: bool = True):

    """
    Returns all the regriddable variables in an input file
    """
    
    if is_tiled: input_file += ".tile1"
    input_file += ".nc"
    
    #load data file
    #xarray gives an error if variables to drop do not exist in the file.  The errors="ignore" fixes that
    dataset = xr.load_dataset(str(input_file)).drop_vars(non_regriddable_variables, errors="ignore")

    #list of variables to regrid, only multi-dimensional data will be regridded
    regrid_vars_string = " ".join([variable for variable in dataset if len(dataset[variable].sizes)>1])

    return regrid_vars_string
    

def regrid_xy(pp_yamlfile: str,
              remap_file: str = None,
              only_thesecomponents: list[int] = None,
              input_date: str = None,
              input_dir: str = None,
              output_dir: str = None):
    
    """
    Remaps variables for each component element in the post-processing yaml file.
    If regrid_thesecomponents is not specified, regrid_xy will regrid all components.
    To regrid only specific components, regrid_thesecomponents must have the element number
    of the component to regrid.      
    """
    
    #load pp_yaml_file to a dictionary
    with open(pp_yamlfile, 'r') as openedfile:
        ppyaml = yaml.safe_load(openedfile)

    #retrieve the grid_spec tar filename from ppyaml
    pp_grid_spec_tar = ppyaml['postprocess']['settings']['pp_grid_spec']
    
    #untar grid_spec tar file
    if tarfile.is_tarfile(pp_grid_spec_tar):
        with tarfile.open(pp_grid_spec_tar, 'r') as tar: tar.extractall()         

    #TODO check if grid_spec.nc exists
    grid_spec = "grid_spec.nc"

    #set input and output directory names if not specified 
    if input_dir is None: input_dir = ppyaml['directories']["history_dir"]
    if output_dir is None: output_dir = ppyaml['directories']["pp_dir"]    

    #get components to remap 
    if only_thesecomponents is None:
        #regrid all components
        components = ppyaml['postprocess']['components']
    else:
        #regrid only components specified in the list only_thesecomponents
        components = [ppyaml['postprocess']['components'][i] for i in regrid_thesecomponents]

    #iterate over components that will be regridded
    for component in components:

        #skip if postprocessing is turned off for the component
        if component['postprocess_on'] is False: continue

        #get input mosaic filename corresponding to the inputRealm
        input_mosaic = get_input_mosaic(grid_spec, component['inputRealm'])
        tiled = is_tiled(input_mosaic)
        
        #get interp_method: bilinear, conserve_interp1, conserve_interp2
        interp_method = component['interpMethod']

        #get output grid dimensions
        [output_nlat, output_nlon] = [int(dims) for dims in component['xyInterp'].split(",")]
        
        #directory holding the static file that contains the input grid cell areas
        associated_file_dir = input_dir

        #remap each history file in component.  The history file will be
        #specified as, e.g., "atmos_daily_cmip"
        for history_dict in component['sources']:

          history_file = history_dict["history_file"]

          #pretend the date to the history_file so that, e.g.,
          input_file = get_input_file(history_file, input_date)
          
          #get all fields to regrid
          scalar_field = get_scalar_fields(input_file, tiled)        
          
          #get remap file and name that will be cached
          remap_cache_file = get_remap_file(remap_file, input_mosaic, output_nlat, output_nlon, interp_method)
            
          output_file = "this"
            
          fregrid_command = ['fregrid',
                              '--debug',
                              '--standard_dimension',
                              '--input_mosaic', input_mosaic,
                              '--input_dir', input_dir,
                              '--input_file', input_file,
                              '--associated_file_dir', associated_file_dir,
                              '--interp_method', interp_method,
                              '--remap_file', remap_cache_file,
                              '--nlon', output_nlon,
                              '--nlat', output_nlat,
                              '--scalar_field', scalar_field,
                              '--output_dir', output_dir,
                              '-output_file', output_file]
          print(fregrid_command)
                               
            #fregrid_proc = subprocess.run(fregrid_command, check=True)
