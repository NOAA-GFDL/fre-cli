import logging
from pathlib import Path
import shutil
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


def get_input_mosaic(datadict: dict) -> type[Path]:

    """
    Gets the input mosaic filename from the grid_spec file.
    If the input mosaic file is not in input_dir, this function will copy the input mosaic file to input_dir.

    :datadict: dictionary containing relevant regrid parameters
    :type datadict: dict
    :raises IOError: Error if the input mosaic file cannot be found in the current or input directory

    :return: input_mosaic file path as a Path object
    :rtype: Path

    .. note:: The input mosaic filename is a required input argument for fregrid.
              The input mosaic contains the input grid information.
    """

    input_dir = datadict["input_dir"]
    grid_spec = datadict["grid_spec"]

    match datadict["component"]["inputRealm"]:
        case "atmos": mosaic_key = "atm_mosaic_file"
        case "ocean": mosaic_key = "ocn_mosaic_file"
        case "land": mosaic_key = "lnd_mosaic_file"

    mosaic_file = Path(str(xr.load_dataset(grid_spec)[mosaic_key].values.astype(str)))

    if not (input_dir / mosaic_file).exists():
        if mosaic_file.exists():
            shutil.copy(mosaic_file, input_dir / mosaic_file)
            fre_logger.info(f"Copying {mosaic_file} to input directory {input_dir}")
        else:
            raise IOError((f"Cannot find input mosaic file {mosaic_file} "
                            "in current or input directory {input_dir}"))

    return input_dir / mosaic_file


def get_grid_spec(datadict: dict) -> type[Path]:
    """
    Gets the grid_spec.nc file from the tar file specified in
    yaml["postprocess"]["settings"]["pp_grid_spec"]

    :datadict: dictionary containing relevant regrid parameters
    :type datadict: dict

    :raises IOError:  Error if grid_spec.nc file cannot be found in the tar file

    :return: grid_spec file path as a Path object
    :rtype: Path

    .. note:: All grid_spec files are expected to be named "grid_spec.nc".
              The grid_spec file is required in order to obtain the
              input mosaic filename
    """

    grid_spec = Path("grid_spec.nc")

    pp_grid_spec_tar = datadict["yaml"]["postprocess"]["settings"]["pp_grid_spec"]

    # untar grid_spec tar file
    if tarfile.is_tarfile(pp_grid_spec_tar):
        with tarfile.open(pp_grid_spec_tar, "r") as tar:
            tar.extractall()

    if not grid_spec.exists():
        raise IOError(f"Cannot find {grid_spec} in tar file {pp_grid_spec_tar}")

    return grid_spec


def get_input_file_argument(datadict: dict, history_file: str) -> str:

    """
    Formats the input file name where the input file contains the variable data that will be regridded.

    :datadict: dictionary containing relevant regrid parameters
    :type datadict:dict
    :history_file: history file type
    :type history_file: str

    :return: formatted input file name
    :rtype: str

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

    :return: remap file path as a Path object
    :rtype: Path

    ..note:: remap_file is a required fregrid argument.  If the remap_file exists, then
             fregrid will read in the remapping parameters (the exchange grid for conservative methods)
             from the remap_file for regridding the variables.  If the remap_file does not exist,
             fregrid will compute the remapping parameters and save them to the remap_file
    """

    input_dir = datadict["input_dir"]
    input_mosaic = datadict["input_mosaic"]
    nlon = datadict["output_nlon"]
    nlat = datadict["output_nlat"]
    interp_method = datadict["interp_method"]

    remap_file = Path(f"{input_mosaic.stem}X{nlon}by{nlat}_{interp_method}.nc")

    if not (input_dir / remap_file).exists():
        if (remap_file).exists():
            shutil.copy(remap_file, input_dir / remap_file)
            fre_logger.info(f"Remap file {remap_file} copied to input directory {input_dir}")
        else:
            fre_logger.info(
                f"Cannot find specified remap_file {remap_file}\n"
                "Remap file {remap_file} will be generated and saved to the input directory"
                f"{input_dir}"
            )

    return input_dir / remap_file


def get_scalar_fields(datadict: dict) -> tuple[str, bool]:

    """
    Returns the scalar_fields argument for fregrid.
    Scalar_fields is a string of comma separated list of variables
    that will be regridded

    :datadict: dictionary containing relevant regrid parameters
    :type datadict: dict

    :return: tuple of a string of scalar fields and a boolean indicating whether regridding is needed
    :rtype: tuple[str, bool]

    ..note:: With the exception of the variables in the list
             non_regriddable_variables, all variables
             will be regridded.
    """

    mosaic_file = datadict["input_mosaic"]

    extension = ".tile1.nc" if xr.load_dataset(mosaic_file).sizes["ntiles"] > 1 else ".nc"
    input_file = datadict["input_dir"] / Path(datadict["input_file"] + extension)

    # xarray gives an error if variables in non_regriddable_variables do not exist in the dataset
    # The errors="ignore" overrides the error
    dataset = xr.load_dataset(input_file).drop_vars(non_regriddable_variables, errors="ignore")

    regrid = True
    if len(dataset) == 0:
        fre_logger.warning(f"No variables found in {input_file} to regrid")
        regrid = False

    return ",".join([variable for variable in dataset]), regrid


def write_summary(datadict):

    """
    Logs a summary of the component that will be regridded in a human-readable format
    This function will log only if the logging level is set to INFO or lower

    :datadict: dictionary containing relevant regrid parameters
    :type datadict: dict
    """

    fre_logger.info("COMPONENT SUMMARY")
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


def regrid_xy(
    yamlfile: str,
    input_dir: str,
    output_dir: str,
    components: list[str] = None,
    input_date: str = None,
):

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

    # load yamlfile to thisyaml
    with open(yamlfile, "r") as openedfile:
        thisyaml = yaml.safe_load(openedfile)

    # save arguments to datadict
    datadict["yaml"] = thisyaml
    datadict["grid_spec"] = get_grid_spec(datadict)
    datadict["input_dir"] = Path(input_dir)
    datadict["output_dir"] = Path(output_dir)
    datadict["input_date"] = input_date

    # get list of components to regrid
    components_list = thisyaml["postprocess"]["components"]
    if components is not None:
        for component in components_list:
            if component["type"] not in components:
                components_list.remove(component)

    # submit fregrid job for each component
    for component in components_list:

        if component["postprocess_on"] is False:
            fre_logger.warning(f"skipping component {component['type']}")
            continue

        datadict["component"] = component
        datadict["input_mosaic"] = get_input_mosaic(datadict)
        datadict["output_nlat"], datadict["output_nlon"] = component["xyInterp"].split(",")
        datadict["interp_method"] = component["interpMethod"]

        # iterate over each history file in the component
        for history_dict in component["sources"]:

            datadict["input_file"] = get_input_file_argument(datadict, history_dict["history_file"])
            datadict["scalar_field"], regrid = get_scalar_fields(datadict)

            if not regrid: continue

            datadict["remap_file"] = get_remap_file(datadict)

            write_summary(datadict)

            fregrid_command = [
                "fregrid",
                "--debug",
                "--standard_dimension",
                "--input_dir", str(datadict["input_dir"]),
                "--input_mosaic", str(datadict["input_mosaic"]),
                "--input_file", datadict["input_file"],
                "--interp_method", datadict["interp_method"],
                "--remap_file", str(datadict["remap_file"]),
                "--nlon", datadict["output_nlon"],
                "--nlat", datadict["output_nlat"],
                "--scalar_field", datadict["scalar_field"],
                "--output_dir", str(datadict["output_dir"]),
            ]

            fregrid_job = subprocess.run(fregrid_command, capture_output=True, text=True)

            if fregrid_job.returncode == 0:
                fre_logger.info(fregrid_job.stdout.split("\n")[-3:])
            else:
                raise RuntimeError(fregrid_job.stderr)
