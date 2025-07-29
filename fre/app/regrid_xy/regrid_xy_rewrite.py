from pathlib import Path
import tarfile
import xarray as xr
import yaml

#dictionary that maps inputRealm from the pp_yaml the variable name
#holding the mosaic filenames in the gridspec file
#For example, in gridspec.nc, atm_mosaic_file = C96_mosaic.nc
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

def get_input_dimensions(input_file):

    """
    Retrieves the grid dimension 'nx' and 'ny' from the input_file
    Returns the number of grid cells on the A-grid
    """

      grid = xr.load_dataset(input_file)
      nlon = grid.sizes['nx']//2
      nlat = grid.sizes['ny']//2

      return [nlat, nlon]
  

def get_input_file(input_file: str = None, input_date: str = ''):

    """
    Intakes the prefix of the input_file returns the filename
    pretended with the input_date so that the filename is YYYYMMDD.input_file.  
    For a cubed sphere, fregrid will regrid the tile files YYYYMMDD.input_file.tile#.nc
    """
    
    #FRE-NCTools expects input files without the .nc extension
    if ".nc" in input_file: input_file = input_file[:-3]

    return f"{inputdate}.{inputfile}"


def get_input_mosaic(gridspec: str, input_realm: str):

    """
    Intakes the input_realm field from the pp yaml and returns
    the type of mosaic file
    """
    
    mosaic_key = map_mosaicfile[input_realm]
    return str(xr.load_dataset(grid_spec)[mosaic_key].values.astype(str))


def get_remap_file(remap_file: str, output_dir: str, input_mosaic, output_nlat: int, output_nlon: int):

    if remap_file is not None:
        try:
            shutil.copy(remap_file, remap_file.split('/').pop())
        except Exception as exc:
            raise OSError("remap_file={remap_file} could not be copied to work dir") from exc

        remap_file= f"fregrid_remap_file_{output_nlon}_by_{output_nlat}.nc"
        remap_cache_file = f"{output_dir}/{input_moasic}X{nlon}_{nlat}_conservative{order}.nc"

        fre_logger.info(f'remap_file = {remap_file}\n')
        fre_logger.info(f'NOTE: Will generate remap file and cache to {remap_cache_file}')
        
        return remap_file, remape_cache_file


def get_scalar_fields(input_file: str):

    """
    Returns all the regriddable variables in an input file
    """
    
    #load data file
    dataset = xr.load_dataset(input_file).drop_vars(non_regriddable_variables, errors="ignore")

    #list of variables to regrid, only multi-dimensional data will be regridded
    regrid_vars_string = " ".join([variable for variable in dataset if len(dataset[variable].sizes)>1])

    return regrid_vars_string
    

def regrid_xy(pp_yaml_file: dict,
              remap_file: str = None,
              regrid_thesecomponents: list[int] = None,
              input_date: str = None,
              input_dir: str = None,
              output_dir: str = None):
    
    #load pp_yaml_file to a dictionary
    with open(pp_yaml_file, 'r') as openedfile:
        ppyaml = yaml.safe_load(openedfile)

    #untar gridspec tar file
    pp_gridspec_tar = ppyaml['postprocess']['settings']['pp_grid_spec']

    if tarfile.is_tarfile(pp_gridspec_tar):
        with tarfile.open(pp_gridspec_tar, 'r') as tar: tar.extractall()         

    #set input and output directories
    input_dir = ppyaml['directories']["history_dir"]
    output_dir = ppyaml['directories']["pp_dir"]

    #set remap file #f"{output_dir}/remap.nc"
    remap_file = get_remap_file(remap_file, nlon, nlat)
    

    #get components to remap
    if regrid_thesecomponents is None:
        components = ppyaml['postprocess']['components']
    else:
        components = [ppyaml['postprocess']['components'][i] for i in regrid_thesecomponents]

    #iterate over components to regrid
    for component in components:

        #skip is postprocessing is turned off for the component
        if component['postprocess_on'] is False: continue

        #get input mosaic file corresponding to the inputRealm
        input_mosaic = get_input_mosaic(gridspec, component['inputRealm'])

        #get interp_method: bilinear, conserve_interp1, conserve_interp2
        interp_method = component['interpMethod']

        #get output grid dimensions
        [output_nlat, output_nlon] = component['xyInterp']
        
        #static file with input grid areas
        associated_file_dir = input_dir

        #get history file prefixes to regrid
        for ifile in component['sources']['history_file']:

            #get names of history files (labeled by input_date)
            input_file = get_input_file(input_file, input_date)

            #get input grid dimensions
            [input_nlat, input_nlon] = get_input_dimensions(input_file)

            #get remap file and name that will be cached
            remap_file, remap_cache_file = get_remap_file(remap_file, input_mosaic, output_nlat, output_nlon)
            
            #get all fields to regrid
            scalar_field = get_scalar_fields(input_file)        

            fregrid_command = ['fregrid',
                               '--debug',
                               '--standard_dimension',
                               '--input_mosaic', input_mosaic
                               '--input_dir', input_dir,
                               '--input_file', input_file,
                               '--associated_file_dir', associated_file_dir,
                               '--interp_method', interp_method,
                               '--remap_file', remap_file,
                               '--nlon', output_nlon,
                               '--nlat', output_nlat,
                               '--scalar_field', scalar_field,
                               '-output_file', output_file
            ]
                               
            fregrid_proc = subprocess.run(fregrid_command, check=True)
            
regrid_xy('./c96L65_am5f8d6r3_amip.yaml')
