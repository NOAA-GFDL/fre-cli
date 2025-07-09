from pathlib import Path
import tarfile
import xarray as xr
import yaml

map_mosaicfile = dict(atmos = 'atm_mosaic_file',
                      aerosol = 'atm_mosaic_file',
                      ocean = 'ocn_mosaic_file',
                      land = 'lnd_mosaic_file')

non_regriddable_variables = [
    'geolon_c', 'geolat_c', 'geolon_u', 'geolat_u', 'geolon_v', 'geolat_v',
    'FA_X', 'FA_Y', 'FI_X', 'FI_Y', 'IX_TRANS', 'IY_TRANS', 'UI', 'VI', 'UO', 'VO',
    'wet_c', 'wet_v', 'wet_u', 'dxCu', 'dyCu', 'dxCv', 'dyCv', 'Coriolis',
    'areacello_cu', 'areacello_cv', 'areacello_bu', 'average_T1','average_T2',
    'average_DT','time_bnds']


def get_input_mosaic(gridspec: str, input_realm: str):

    mosaic_key = map_mosaicfile[input_realm]
    return str(xr.load_dataset(grid_spec)[mosaic_key].values.astype(str))


def get_input_file(input_file: str = None, input_date: str = ''):

    if ".nc" in input_file: input_file = input_file[:-3]
    return f"{inputdate}.{inputfile}"
    

def get_scalar_fields(input_file: str):

    #load data file
    dataset = xr.load_dataset(input_file).drop_vars(non_regriddable_variables, errors="ignore")

    #list of variables to regrid, only multi-dimensional data will be regridded
    regrid_vars_string = " ".join([variable for variable in dataset if len(dataset[variable].sizes)>1])

    return regrid_vars_string
    

def regrid_xy(input_file: str = None, input_date: str = None, input_dir: str = None,
              output_dir: str = None, remap_file: str = None, pp_yamlfile: str = None, gridspec: str = None):

    #load yaml
    with open(pp_yamlfile, 'r') as openedfile:
        ppyaml = yaml.safe_load(openedfile)

    #untar gridspec tar file
    pp_gridspec_tar = thisyaml['postprocess']['settings']['pp_grid_spec']
    if tarfile.is_tarfile(pp_gridspec_tar):
        with tarfile.open(pp_gridspec_tar, 'r') as tar: tar.extractall()        

    if gridspec is None: gridspec = 'grid_spec.nc'

    if input_dir is None: input_dir = ppyaml['directories']["history_dir"]
    if output_dir is None: output_dir = ppyaml['directories']["pp_dir"]
    if remap_file is None: remap_file = f"{output_dir}/remap.nc"
        
    for component in ppyaml['postprocess']['components']:

        if component['postprocess_on'] is False: continue

        #input_mosaic will be dataset['atmos_mosaic_file'], dataset['ocn_mosaic_file'], or dataset['lnd_mosaic_file']
        #depending on the inputRealm
        input_mosaic = get_input_mosaic(gridspec, component['inputRealm'])

        #get interp_method: bilinear, conserve_interp1, conserve_interp2
        interp_method = thisyaml['interpMethod']

        #get output grid dimensions
        [nlat, nlon] = component['xyInterp']

        #static file with input grid areas
        #should be changed to extract the dir from the input file in the global attribute
        associated_file_dir = input_dir
        
        for ifile in component['sources']['history_file']:

            input_file = get_input_file(input_file, input_date)
            
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
                               '--nlon', nlon,
                               '--nlat', nlat,
                               '--scalar_field', scalar_field,
                               '-output_file', output_file
            ]
                               
            fregrid_proc = subprocess.run( fregrid_command, check = True )
            
regrid_xy('./c96L65_am5f8d6r3_amip.yaml')
