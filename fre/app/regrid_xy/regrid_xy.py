import logging
import os
from pathlib import Path
import subprocess
import tarfile
import xarray as xr
import yaml

fre_logger = logging.getLogger(__name__)

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

    :datadict: dictionary containing relevant regrid parameters
    :type datadict: dict

    :raises IOError:  Error if grid_spec.nc file cannot be found in the 
                      current directory

    :return: grid_spec filename
    :rtype: str

    .. note:: All grid_spec files are expected to be named "grid_spec.nc".
              The grid_spec file is required in order to determine the
              input mosaic filename
    """

    #grid spec filename
    grid_spec = "grid_spec.nc"

    #get tar file containing the grid_spec file
    pp_grid_spec_tar = datadict["yaml"]["postprocess"]["settings"]["pp_grid_spec"]

    #untar grid_spec tar file into the current work directory    
    if tarfile.is_tarfile(pp_grid_spec_tar):
        with tarfile.open(pp_grid_spec_tar, "r") as tar:
            tar.extractall()

    #error if grid_spec file is not found after extracting from tar file
    if not Path(grid_spec).exists():
        raise IOError(f"Cannot find {grid_spec} in tar file {pp_grid_spec_tar}")

    return grid_spec


def get_input_mosaic(datadict: dict) -> str:

    """
    Gets the input mosaic filename from the grid_spec file.

    :datadict: dictionary containing relevant regrid parameters
    :type datadict: dict
    :raises IOError: Error if the input mosaic file cannot be found in the 
                     current work directory

    :return: input_mosaic file 
    :rtype: str

    .. note:: The input mosaic filename is a required input argument for fregrid.
              The input mosaic contains the input grid information.
    """

    grid_spec = datadict["grid_spec"]

    #gridspec variable name holding the mosaic filename information
    match datadict["inputRealm"]:
        case "atmos": mosaic_key = "atm_mosaic_file"
        case "ocean": mosaic_key = "ocn_mosaic_file"
        case "land": mosaic_key = "lnd_mosaic_file"

    #get mosaic filename
    with xr.open_dataset(grid_spec) as dataset:
        mosaic_file = str(dataset[mosaic_key].data.astype(str))

    #check if the mosaic file exists in the current directory
    if not Path(mosaic_file).exists():
        raise IOError(f"Cannot find mosaic file {mosaic_file} in current work directory {work_dir}")

    return mosaic_file


def get_input_file(datadict: dict, source: str) -> str:

    """
    Formats the input file name where the input file contains the variable data that will be regridded.

    :datadict: dictionary containing relevant regrid parameters
    :type datadict:dict
    :source: history file type
    :type source: str

    :return: formatted input file name
    :rtype: str

    .. note:: The input filename is a required argument for fregrid and refer to the history files containing the
    data that will be regridded.  A history file is typically named, for example, as
    20250805.atmos_daily_cmip.tile1.nc, 20250805.atmos_daily_cmip.tile2.nc, ..., 20250805.atmos_daily_cmip.tile6.nc,
    The yaml configuration does not contain the exact history filenames and the filenames need to be constructed by
    (1) extracting the history file "type" from the yaml configuration.  This type corresponds to the field value of
    yaml["postprocess"]["components"]["sources"]["source"] and, for example, be "atmos_daily_cmip"
    (2) prepending YYYYMMDD to the filename.  This function will prepend the date if the date string was passed to the
    entrypoint function regrid_xy of this module:  i.e., this function will return "20250805.atmos_daily_cmip"
    (3) Fregrid will append the tile numbers ("tile1.nc") for reading in the data
    """

    input_date = datadict["input_date"]
    return source if input_date is None else f"{input_date}.{source}"


def get_remap_file(datadict: dict) -> str:

    """
    Determines the remap filename based on the input mosaic filename, output grid size, and
    conservative order.  For example, this function will return the name
    C96_mosaicX180x288_conserve_order1.nc where the input mosaic filename is C96_mosaic.nc and
    the output grid size has 180 longitude cells and 288 latitude cells.

    The remap_file will be read from, or outputted to the remap_dir.

    :datadict: dictionary containing relevant regrid parameters
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
            (f"Cannot find remap_file {remap_file}\n"
             f"Remap file {remap_file} will be generated and saved to directory {remap_dir}"
            )
        )

    return str(remap_file)


def get_scalar_fields(datadict: dict) -> tuple[str, bool]:

    """
    Returns the scalar_fields argument for fregrid.
    Scalar_fields is a string of comma separated list of variables
    that will be regridded

    :datadict: dictionary containing relevant regrid parameters
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
    with xr.open_dataset(input_dir/input_file) as dataset:
        regrid_dataset = dataset.drop_vars(non_regriddable_variables, errors="ignore")

    if len(regrid_dataset) == 0:
        fre_logger.warning(f"No variables found in {input_file} to regrid")
        return "None", False

    return ",".join([variable for variable in regrid_dataset]), True


def write_summary(datadict):

    """
    Logs a summary of the component that will be regridded in a human-readable format
    This function will log only if the logging level is set to INFO or lower

    :datadict: dictionary containing relevant regrid parameters
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
    Submits a fregrid job for the specified source data file.

    :yamlfile: yaml file containing specifications for yaml["postprocess"]["settings"]["pp_grid_spec"]
               and yaml["postprocess"]["components"]
    :input_dir: Name of the input directory containing the input/history files,
                Fregrid will look for all input history files in input_dir.
    :output_dir: Name of the output directory where fregrid outputs will be saved
    :work_dir: Directory that will contain the extracted files from the grid_spec tar 
    :remap_dir: Directory that will contain the generated remap file
    :Source: The stem of the history file to regrid
    :Input_date: Datestring in the format of YYYYMMDD that corresponds to the date prefix of the history files,
                 e.g., input_date=20250730 where the history filename is 20250730.atmos_month_aer.tile1.nc

    .. note:  All directories should be in absolute paths
    """

    #check if input_dir exists
    if not Path(input_dir).exists():
        raise RuntimeError(f"Input directory {input_dir} containing the input data files does not exist")

    #check if output_dir exists
    if not Path(output_dir).exists():
        raise RuntimeError((f"Output directory {output_dir} where regridded data"
                            "will be outputted does not exist"))

    #get current directory
    curr_dir = os.getcwd()

    #change into work directory
    try:
        os.chdir(work_dir)
    except Exception:
        raise RuntimeError(f"Cannot change into work directory {work_dir}")
    
    #initialize datadict
    datadict = {}

    # load yamlfile to yamldict
    with open(yamlfile, "r") as openedfile:
        yamldict = yaml.safe_load(openedfile)

    # save arguments to datadict
    datadict["yaml"] = yamldict
    datadict["grid_spec"] = get_grid_spec(datadict)
    datadict["input_dir"] = input_dir
    datadict["output_dir"] = output_dir
    datadict["work_dir"] = work_dir
    datadict["remap_dir"] = remap_dir
    datadict["input_date"] = input_date

    components = []
    for component in yamldict["postprocess"]["components"]:
        for this_source in component["sources"]:
            if this_source["history_file"] == source:
                components.append(component)

    # submit fregrid job for each component
    for component in components:
        
        # skip component if postprocess_on = False 
        if not component["postprocess_on"]:
            fre_logger.warning((f"postprocess_on=False for {source} in component {component['type']}."
                                "Skipping {source}"))
            continue
        
        datadict["inputRealm"] = component["inputRealm"]
        datadict["input_mosaic"] = get_input_mosaic(datadict)
        datadict["output_nlat"], datadict["output_nlon"] = component["xyInterp"].split(",")
        datadict["interp_method"] = component["interpMethod"]
        datadict["remap_file"] = get_remap_file(datadict)        
        datadict["input_file"] = get_input_file(datadict, source)
        datadict["scalar_field"], regrid = get_scalar_fields(datadict)
        
        # skip if there are no variables to regrid
        if not regrid: continue

        #write useful information
        write_summary(datadict)

        #construct fregrid command
        fregrid_command = [
            "fregrid",
            "--debug",
            "--standard_dimension",
            "--input_dir", input_dir,
            "--input_mosaic", datadict["input_mosaic"],
            "--input_file", datadict["input_file"],
            "--interp_method", datadict["interp_method"],
            "--remap_file", datadict["remap_file"],
            "--nlon", datadict["output_nlon"],
            "--nlat", datadict["output_nlat"],
            "--scalar_field", datadict["scalar_field"],
            "--output_dir", output_dir,
        ]

        #execute fregrid command
        fregrid_job = subprocess.run(fregrid_command, capture_output=True, text=True)

        #print job useful information
        if fregrid_job.returncode == 0:
            fre_logger.info(fregrid_job.stdout.split("\n")[-3:])
        else:
            raise RuntimeError(fregrid_job.stderr)

    #change to original directory
    os.chdir(curr_dir)
