import logging
import os
from pathlib import Path
import pprint
import subprocess
import tarfile
import xarray as xr
import yaml

from fre.app import helpers

fre_logger = logging.getLogger(__name__)

# it appears that fregrid believes the grid_spec file must have a datetime attached to it, like
#     YYYYMMDD.grid_spec.tile
# this is behavior in noaa-gfdl::fre-nctools==2022.02.01 that can't be changed, and so must be worked around.
# hence, "ATTACH_LEGACY_DT"
ATTACH_LEGACY_DT = True

# list of variables/fields that will not be regridded
non_regriddable_variables = [
    "geolon_c",
    "geolat_c",
    "geolon_u",
    "geolat_u",
    "geolon_v",
    "geolat_v",
    "FA_X",
    "FA_Y",
    "FI_X",
    "FI_Y",
    "IX_TRANS",
    "IY_TRANS",
    "UI",
    "VI",
    "UO",
    "VO",
    "wet_c",
    "wet_v",
    "wet_u",
    "dxCu",
    "dyCu",
    "dxCv",
    "dyCv",
    "Coriolis",
    "areacello_cu",
    "areacello_cv",
    "areacello_bu",
    "average_T1",
    "average_T2",
    "average_DT",
    "time_bnds",
]


def get_grid_spec(datadict: dict) -> str:

    """
    Gets the grid_spec.nc file from the tar file specified in
    yaml["postprocess"]["settings"]["pp_grid_spec"]

    :param datadict: dictionary containing relevant regrid parameters
    :type datadict: dict

    :raises IOError:  Error if grid_spec.nc file cannot be found in the
                      current directory

    :return: grid_spec filename
    :rtype: str

    .. note:: All grid_spec files are expected to be named "grid_spec.nc".
              The grid_spec file is required in order to determine the
              input mosaic filename
    """
    
    grid_spec = str(Path("grid_spec.nc").resolve())
    fre_logger.info('grid spec filename is: %s', grid_spec)

    pp_grid_spec_tar = datadict["yaml"]["postprocess"]["settings"]["pp_grid_spec"]
    fre_logger.info('grid spec tar archive file name is: %s', pp_grid_spec_tar)

    fre_logger.debug('checking if %s is a tar file...', pp_grid_spec_tar)
    if tarfile.is_tarfile(pp_grid_spec_tar):
        
        fre_logger.debug('it is a tar file! attempting top open %s', pp_grid_spec_tar)
        with tarfile.open(pp_grid_spec_tar, "r") as tar:
            
            fre_logger.debug('opened! about to extract all from opened tar file object into %s', os.getcwd())
            tar.extractall()
            fre_logger.debug('everything extracted!')
            fre_logger.debug('contents extracted are ... %s', str(os.listdir(os.getcwd())) )
            
    #error if grid_spec file is not found after extracting from tar file
    if not Path(grid_spec).exists():
        raise IOError(f"Cannot find {grid_spec} in tar file {pp_grid_spec_tar}")
    
    fre_logger.debug('grid_spec = %s exists!', grid_spec)

    grid_spec_dt_symlink = None
    if ATTACH_LEGACY_DT:
        fre_logger.warning('creating symlink to account for legacy fre-nctools 2022.02.01 behavior')
        grid_spec_dt_symlink = Path(grid_spec).parent / f'{datadict["input_date"]}.grid_spec.nc'
        
        fre_logger.warning('grid_spec_dt_symlink = %s', grid_spec_dt_symlink)

        # what in the ever loving demon magic is going on here???
        try:
            grid_spec_dt_symlink.symlink_to(Path(grid_spec))
        except FileExistsError:
            pass

        # i am sorry python gods, i have failed out
        if grid_spec_dt_symlink.exists():
            fre_logger.warning('great? how did this happen?')

        # continued inexplicable success.
        if grid_spec_dt_symlink.is_symlink():
            fre_logger.warning('symlink created: %s', grid_spec_dt_symlink)
        else:
            raise Exception('problem with accounting for legacy fregrid/fre-nctools behavior, symbolic link creation '
                          'as-intended-side-effect failed. consult life choices.')
        
    return grid_spec, grid_spec_dt_symlink


def get_input_mosaic(datadict: dict) -> str:

    """
    Gets the input mosaic filename from the grid_spec file.

    :param datadict: dictionary containing relevant regrid parameters
    :type datadict: dict
    :raises IOError: Error if the input mosaic file cannot be found in the
                     current work directory

    :return: input_mosaic file
    :rtype: str

    .. note:: The input mosaic filename is a required input argument for fregrid.
              The input mosaic contains the input grid information.
    """
    grid_spec = datadict["grid_spec"]
    fre_logger.info('grid_spec is: %s', grid_spec)
    if not Path(grid_spec).exists():
        raise FileNotFoundError(f'grid_spec = {grid_spec} does not exist')

    #gridspec variable name holding the mosaic filename information
    match datadict["inputRealm"]:
        case "atmos": mosaic_key = "atm_mosaic_file"
        case "ocean": mosaic_key = "ocn_mosaic_file"
        case "land": mosaic_key = "lnd_mosaic_file"

    #get mosaic filename
    with xr.open_dataset(grid_spec) as dataset:
        mosaic_file = str(
            Path(
                str(
                    dataset[mosaic_key].data.astype(str)
                )
            ).resolve()
        )

    #check if the mosaic file exists in the current directory
    if not Path(mosaic_file).exists():
        raise IOError(f"Cannot find mosaic file {mosaic_file} in current work directory {work_dir}")

    return mosaic_file


def get_input_file(datadict: dict, source: str, input_dir: str) -> str:
    """
    Formats the input file name where the input file contains the variable data that will be regridded.

    :param datadict: dictionary containing relevant regrid parameters
    :type datadict:dict
    :param source: history file type
    :type source: str
    :param input_dir: input file directory

    :return: formatted full path to input file name
    :rtype: str

    .. note:: The input filename is a required argument for fregrid and refer to the history files containing
              the data that will be regridded.  A history file is typically named, for example, as
              20250805.atmos_daily_cmip.tile1.nc, 20250805.atmos_daily_cmip.tile2.nc, ...,
              The yaml configuration does not contain the exact history filenames and the filenames need to be
              constructed by:
              (1) extracting the history file "type" from the yaml configuration.  This type corresponds
              to the field value of yaml["postprocess"]["components"]["sources"]["source"] and, for example,
              be "atmos_daily_cmip"
              (2) prepending YYYYMMDD to the filename.  This function will prepend the date if the date
              string was passed to the entrypoint function regrid_xy of this module:  i.e., this function
              will return "20250805.atmos_daily_cmip"
              (3) Fregrid will append the tile numbers ("tile1.nc") for reading in the data
    """
    fre_logger.debug('attempting to read input_date key from datadict')
    input_date = datadict["input_date"]
    if input_date is None:
        fre_logger.debug('input_date is None, resolve source = %s and return that absolute path', source)
        input_file = f"{input_dir}/{source}"
    else:
        fre_logger.debug('input_date = %s, returning absolute path based on that', input_date)
        input_file = f"{input_dir}/{input_date}.{source}"

    fre_logger.debug('returning %s', input_file)
    return input_file

def get_remap_file(datadict: dict) -> str:

    """
    Determines the remap filename based on the input mosaic filename, output grid size, and
    conservative order.  For example, this function will return the name
    C96_mosaicX180x288_conserve_order1.nc where the input mosaic filename is C96_mosaic.nc and
    the output grid size has 180 longitude cells and 288 latitude cells.

    The remap_file will be read from, or outputted to the remap_dir.

    :param datadict: dictionary containing relevant regrid parameters
    :type datadict: dict

    :return: remap filename
    :rtype: str

    .. note:: remap_file is a required fregrid argument.  If the remap_file exists, then
              fregrid will read in the remapping parameters (the exchange grid for conservative methods)
              from the remap_file for regridding the variables.  If the remap_file does not exist,
              fregrid will compute the remapping parameters and save them to the remap_file
              for future use.
    """

    input_mosaic = Path(datadict["input_mosaic"])
    remap_dir = Path(datadict["remap_dir"])
    nlon = datadict["output_nlon"]
    nlat = datadict["output_nlat"]
    interp_method = datadict["interp_method"]

    #define remap filename
    remap_file = remap_dir/Path(f"{input_mosaic.stem}X{nlon}by{nlat}_{interp_method}.nc")

    #check if remap file exists in remap_dir
    if not remap_file.exists():
        fre_logger.warning(
            f"Cannot find remap_file {remap_file}\n" \
            f"Remap file {remap_file} will be generated and saved to directory {remap_dir}"
        )

    return str(remap_file)


def get_scalar_fields(datadict: dict) -> tuple[str, bool]:

    """
    Returns the scalar_fields argument for fregrid.
    Scalar_fields is a string of comma separated list of variables
    that will be regridded

    :param datadict: dictionary containing relevant regrid parameters
    :type datadict: dict

    :return: (string of scalar fields, boolean indicating whether regridding is needed)
    :rtype: tuple[str, bool]

    .. note:: With the exception of the variables in the list
              non_regriddable_variables, all variables
              will be regridded.
    """

    input_dir = Path(datadict["input_dir"])
    mosaic_file = datadict["input_mosaic"]
    input_file = datadict["input_file"]

    #add the proper suffix to the input filename
    with xr.open_dataset(mosaic_file) as dataset:
        input_file += ".tile1.nc" if dataset.sizes["ntiles"] > 1 else ".nc"

    # xarray gives an error if variables in non_regriddable_variables do not exist in the dataset
    # The errors="ignore" overrides the error
    #with xr.open_dataset(input_dir/input_file) as dataset:
    with xr.open_dataset(input_file) as dataset:
        regrid_dataset = dataset.drop_vars(non_regriddable_variables, errors="ignore")

    if len(regrid_dataset) == 0:
        fre_logger.warning(f"No variables found in {input_file} to regrid")
        return "None", False

    return ",".join([variable for variable in regrid_dataset]), True


def write_summary(datadict):

    """
    Logs a summary of the component that will be regridded in a human-readable format
    This function will log only if the logging level is set to INFO or lower

    :param datadict: dictionary containing relevant regrid parameters
    :type datadict: dict
    """

    fre_logger.info("COMPONENT SUMMARY")
    fre_logger.info(f"FREGRID work_directory: {datadict['work_dir']}")
    fre_logger.info(f"FREGRID input directory: {datadict['input_dir']}")
    fre_logger.info(f"FREGRID output_directory: {datadict['output_dir']}")
    fre_logger.info(f"FREGRID input mosaic file: {datadict['input_mosaic']}")
    fre_logger.info(f"FREGRID input_file: {datadict['input_file']}")
    fre_logger.info(f"FREGRID remap_file: {datadict['remap_file']}")
    fre_logger.info(
        f"FREGRID output lonxlat grid: {datadict['output_nlon']} X {datadict['output_nlat']}"
    )
    fre_logger.info(f"FREGRID interp method: {datadict['interp_method']}")
    fre_logger.info(f"FREGRID scalar_fields: {datadict['scalar_field']}")


def regrid_xy(yamlfile: str,         
              input_dir: str,        
              output_dir: str,       
              work_dir: str,         
              remap_dir: str,        
              source: str,           
              input_date: str = None,
):

    """
    Calls fregrid to regrid data in the specified source data file.

    :param yamlfile: yaml file containing specifications for yaml["postprocess"]["settings"]["pp_grid_spec"]
                     and yaml["postprocess"]["components"]
    :type yamlfile: str
    :param input_dir: Name of the input directory containing the input/history files,
                      Fregrid will look for all input history files in input_dir.
    :type input_dir: str
    :param output_dir: Name of the output directory where fregrid outputs will be saved
    :type output_dir: str
    :param work_dir: Directory that will contain the extracted files from the grid_spec tar
    :type work_dir: str
    :param remap_dir: Directory that will contain the generated remap file
    :type remap_dir: str
    :param source: The stem of the history file to regrid
    :type source:str
    :param input_date: Datestring where the first 8 characters correspond to YYYYMMDD
                       Input_date[:8] represents the date prefix in the history files,
                       e.g., input_date=20250730T0000Z where the history filename is 
                       20250730.atmos_month_aer.tile1.nc
    :type input_date: str

    .. note:  All directories should be in absolute paths
    """
    fre_logger.info(f"yamlfile   = {yamlfile}")
    fre_logger.info(f"input_dir  = {input_dir}")
    fre_logger.info(f"output_dir = {output_dir}")
    fre_logger.info(f"work_dir   = {work_dir}")
    fre_logger.info(f"remap_dir  = {remap_dir}")
    fre_logger.info(f"source     = {source}")
    fre_logger.info(f"input_date = {input_date}")
    

    fre_logger.debug('checking if input_dir = %s exists', input_dir)
    if not Path(input_dir).exists():
        raise RuntimeError(f"Input directory {input_dir} containing the input data files does not exist")

    fre_logger.debug('checking if output_dir = %s exists', output_dir)
    if not Path(output_dir).exists():
        raise RuntimeError(f"Output directory {output_dir} where regridded data" \
                            "will be outputted does not exist")

    fre_logger.debug('checking if work_dir = %s exists', work_dir)
    if not Path(work_dir).exists():
        raise RuntimeError(f"Specified working directory {work_dir} does not exist")

    fre_logger.debug('cd\'ing to work_dir = %s', work_dir)
    with helpers.change_directory(work_dir):

        fre_logger.debug('initializing datadict')
        datadict = {}

        fre_logger.info( 'opening yamlfile = %s to read into yamldict', yamlfile )
        with open(yamlfile, "r") as openedfile:
            yamldict = yaml.safe_load(openedfile)
            fre_logger.debug( 'the yamldict is: \n%s', pprint.pformat(yamldict) )

        fre_logger.debug( 'saving yamldict fields to datadict' ) 
        datadict["yaml"] = yamldict
        datadict["input_dir"] = input_dir
        datadict["output_dir"] = output_dir
        datadict["work_dir"] = work_dir
        datadict["remap_dir"] = remap_dir
        datadict["input_date"] = input_date[:8]
        fre_logger.info( 'datadict is %s', pprint.pformat(datadict) )

        datadict["grid_spec"], grid_spec_symlink = get_grid_spec(datadict)
        if Path(datadict['grid_spec']).exists():
            fre_logger.info('grid_spec exists here: %s', datadict['grid_spec'])
        


        fre_logger.debug('making component list from yamldict')
        components = []
        for component in yamldict["postprocess"]["components"]:
            for this_source in component["sources"]:
                if this_source["history_file"] == source:
                    components.append(component)
        fre_logger.info('components list is: %s', pprint.pformat(components) )

        fre_logger.debug('assembling fregrid call arguments for each component')
        for component in components:
            fre_logger.debug('component = %s', component)

            fre_logger.debug('checking postprocess_on field in component dict')
            if not component["postprocess_on"]:
                fre_logger.warning(f"postprocess_on=False for {source} in component {component['type']}." \
                                    f"Skipping {source}")
                continue
            
            fre_logger.debug( 'saving component-specific info to datadict' ) 
            datadict["inputRealm"] = component["inputRealm"]
            
            fre_logger.debug('calling get_input_mosaic...')
            datadict["input_mosaic"] = get_input_mosaic(datadict)
            fre_logger.debug('result was %s', datadict["input_mosaic"])
            
            datadict["output_nlat"], datadict["output_nlon"] = component["xyInterp"].split(",")
            datadict["interp_method"] = component["interpMethod"]
            
            fre_logger.debug('calling get_remap_file')
            datadict["remap_file"] = get_remap_file(datadict)
            fre_logger.debug('result is %s', datadict["remap_file"])

            fre_logger.debug('calling get_input_file')
            datadict["input_file"] = get_input_file(datadict, source, input_dir)
            fre_logger.debug('result is %s', datadict["input_file"])

            fre_logger.debug('calling get_scalar_fields')
            datadict["scalar_field"], regrid = get_scalar_fields(datadict)
            fre_logger.debug('result is %s', regrid)
            
            fre_logger.info( 'datadict is now %s', pprint.pformat(datadict) )

            # skip if there are no variables to regrid
            if regrid:
                write_summary(datadict)
            else:
                fre_logger.warning('no variables to regrid, skipping component')
                continue

            fre_logger.debug('constructing fregrid command...')
            fregrid_command = [
                "fregrid",
                "--debug",
                "--standard_dimension",
                "--input_dir", input_dir,
                "--associated_file_dir", input_dir,
                "--input_mosaic", datadict["input_mosaic"],
                "--input_file", datadict["input_file"].split('/')[-1], # no dir with the input file
                "--interp_method", datadict["interp_method"],
                "--remap_file", datadict["remap_file"],
                "--nlon", datadict["output_nlon"],
                "--nlat", datadict["output_nlat"],
                "--scalar_field", datadict["scalar_field"],
                "--output_dir", output_dir,
            ]
            fre_logger.info('the fregrid command is: \n %s',
                            ' '.join(fregrid_command).replace(' --', ' \\\n    --') )

            #execute fregrid command
            fre_logger.debug('using subprocess.run to execute fregrid...')
            fregrid_job = subprocess.run(fregrid_command, capture_output=True, text=True)

            #print job useful information
            if fregrid_job.returncode == 0:
                fre_logger.info(fregrid_job.stdout.split("\n")[-3:])
            else:
                fre_logger.error('fregrid return code is nonzero!')
                fre_logger.error('return code is %s', fregrid_job.returncode)
                fre_logger.error('before error raise: stdout was %s', fregrid_job.stdout)
                raise RuntimeError(fregrid_job.stderr)
