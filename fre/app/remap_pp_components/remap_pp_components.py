"""
Remap/move components that will be post-processed
from one convention, such as history files, to an
updated output directory structure
"""
import os
import subprocess
import glob
from pathlib import Path
import logging
from typing import List
import yaml
from fre.app import helpers

fre_logger = logging.getLogger(__name__)

def verify_dirs(in_dir: str, out_dir: str):
    """
    Verify that the input and output directories exists and are directories

    :param output_dir: output directory
    :type output_dir: str
    :param input_dir: input directory
    :type input_dir: str
    :raises ValueError:
        - input directory invalid
        - output directory invalid

    """

    # Verify input directory exists and is a directory
    if Path(in_dir).is_dir():
        fre_logger.info("Input directory is a valid directory")
    else:
        raise ValueError(f"Error: Input directory {in_dir} does not exist or is not a valid directory")

    # Verify output directory exists and is a directory
    if Path(out_dir).is_dir():
        fre_logger.info("Output directory is a valid directory")
    else:
        raise ValueError(f"Error: Output directory {out_dir} does not exist or is not a valid directory")

def create_dir(out_dir: str, comp: str, freq: str, chunk:str, ens:str, dir_ts: bool) -> str:
    """
    Create the output directory structure

    :param out_dir: output directory
    :type out_dir: str
    :param comp: component that will be post-processed
    :type comp: str
    :param freq: frequency
    :type freq: str
    :param chunk: chunk
    :type chunk: str
    :param ens: ensemble member
    :type ens: str
    :param dir_ts: directory time series workaround
    :type dir_ts: boolean
    :return: output directory structure
    :rtype: str
    """
    # Define dir
    if ens is not None:
        if dir_ts is True:
            dirs = f"{comp}/ts/{ens}/{freq}/{chunk}"
        else:
            dirs = f"{comp}/{ens}/{freq}/{chunk}"
    else:
        if dir_ts is True:
            dirs = f"{comp}/ts/{freq}/{chunk}"
        else:
            dirs = f"{comp}/{freq}/{chunk}"

    # Create dir from outputDir
    os.chdir(out_dir)
    Path(dirs).mkdir(parents=True,exist_ok=True)

    return dirs

def freq_to_legacy(iso_dura: str) -> str:
    """
    Print Bronx-style frequency given an ISO8601 duration
    
    :param iso_dura: frequency
    :type ise_dura: ISO str format
    :raises ValueError: if ISO duration can not be converted to Bronx-style frequency
    :return: bronx-style frequency
    :rtype: str
    """

    if iso_dura=='P1Y':
        freq_legacy = 'annual'
    elif iso_dura=='P1M':
        freq_legacy = 'monthly'
    elif iso_dura=='P3M':
        freq_legacy = 'seasonal'
    elif iso_dura=='P1D':
        freq_legacy = 'daily'
    elif iso_dura=='PT120H':
        freq_legacy = '120hr'
    elif iso_dura=='PT12H':
        freq_legacy = '12hr'
    elif iso_dura=='PT8H':
        freq_legacy = '8hr'
    elif iso_dura=='PT6H':
        freq_legacy = '6hr'
    elif iso_dura=='PT4H':
        freq_legacy = '4hr'
    elif iso_dura=='PT3H':
        freq_legacy = '3hr'
    elif iso_dura=='PT2H':
        freq_legacy = '2hr'
    elif iso_dura=='PT1H':
        freq_legacy = 'hourly'
    elif iso_dura in ['PT30M', 'PT0.5H']:
        freq_legacy = '30min'
    else:
        raise ValueError(f"Could not convert ISO duration '{iso_dura}'")

    return freq_legacy

def chunk_to_legacy(iso_dura: str) -> str:
    """
    Print Bronx-style frequency given an ISO8601 duration

    :param iso_dura: chunk
    :type iso_dura: str
    :return: bronx-style frequency
    :rtype: str 
    """

    if iso_dura[0]=='P':
        if iso_dura[-1:]=='M':
            brx_freq=iso_dura[1]+'mo'
        elif iso_dura[-1:]=='Y':
            brx_freq=iso_dura[1]+'yr'
        else:
            brx_freq = 'error'
    else:
        brx_freq = 'error'

    return brx_freq

def freq_to_date_format(iso_freq: str) -> str:
    """
    Print legacy Bronx-like date template format given a frequency (ISO 8601 duration)

    :param iso_freq: frequency
    :type iso_freq: str
    :raises ValueError: if there is an unknown frequency
    :return: legacy bronx-like date template
    :rtype: str
    """

    if iso_freq=='P1Y':
        return 'CCYY'
    elif iso_freq=='P1M':
        return 'CCYYMM'
    elif iso_freq=='P1D':
        return 'CCYYMMDD'
    elif (iso_freq[:2]=='PT') and (iso_freq[-1:]=='H'):
        return 'CCYYMMDDThh'
    else:
        raise ValueError(f'ERROR: Unknown Frequency {iso_freq}')

def truncate_date(date: str, freq: str) -> str:
    """
    Print a date string to a truncated precision.
        - Accepts a date and frequency
        - Outputs a date string with suitably reduced precision
        - Test cases: '19790101T0000Z P1D', '19800101T0000Z P1M', '19790101T0000Z PT0.5H'
        - Output using cylc (shared.sh calls in job logs): '19790101', '198001', '1979010100'

    :param date: date to begin post-processing
    :type date: ISO string format
    :param freq: frequency
    :type freq: str
    :return: truncated date string 
    :rtype: str
    """

    form = freq_to_date_format(freq)
    fre_logger.info("truncatedateformat: %s", form)
    output = subprocess.Popen(["cylc", "cycle-point", "--template", form, date],
                              stdout=subprocess.PIPE)

    bytedate = output.communicate()[0]
    date=str(bytedate.decode())
    fre_logger.info("truncatedate: %s", date)

    #remove trailing newline
    date=date[:(len(date)-1)]

    #check for and remove 'T' if present
    if not date.isnumeric():
        date=date[:8]+date[-2:]

    return date

def search_files(product: str, var: list, source: str, freq: str,
                 current_chunk: str, begin: str) -> List[str]:
    """
    Pattern match and search for the correct files in the chunk directory

    :param product: ts, av or static
    :type product: str
    :param var: variables
    :type var: list of strings
    :param source: source history files for post-processed component
    :type source: str
    :param begin: date to begin post-processing
    :type begin: ISO string format
    :param current_chunk: current chunk to post-process
    :type current_chunk: str
    :param freq: frequency
    :type freq: str
    :raises ValueError:
        - if specified variable can not be found
        - if product is not ts or av when frequency is not 0
    :return: list of files found
    :rtype: array
    """
    files = []
    # with glob - files found as list
    if freq == "P0Y":
        if var == "all":
            f = glob.glob(f"{source}.*.nc")
            files.extend(f)
        else:
            for v in var:
                fre_logger.info("var: %s", v)
                f = glob.glob(f"{source}.{v}*.nc")
                if not f: #if glob returns empty list
                    raise ValueError("Variable {v} could not be found or does not exist.")
                files.extend(f)
    else:
        if product == "ts":
            date = truncate_date(begin, freq)
            fre_logger.info("date: %s", date)
        elif product == "av":
            date = truncate_date(begin, "P1Y")
        else:
            raise ValueError("Product not set to ts or av.")

        if var == "all":
            f = glob.glob(f"{source}.{date}-*.*.nc")
            files.extend(f)
        else:
            for v in var:
                fre_logger.info("var: %s", v)
                f = glob.glob(f"{source}.{date}-*.{v}*.nc")
                if not f: #if glob returns empty list
                    raise ValueError("Variable {v} could not be found or does not exist.")
                files.extend(f)
        if product == "av" and current_chunk == "P1Y":
            f = glob.glob(f"{source}.{date}.*.nc")
            files.extend(f)

    return files

def get_varlist(comp_info: dict, product: str, req_source: str, src_vars: dict) -> List[str]:
    """
    Retrieve variables listed for a component; save in dictionary for use later

    :param comp_info: dictionary of information about requested component
    :type comp_info: dict
    :param product: static, ts, or av
    :type product: str
    :param req_source: source being looped over
    :type req_source: str
    :param src_vars: dictionary of variables associated with source name
    :type src_vars: dict
    :raises ValueError: if there are no static sources, but the product is set to static
    :return: list of variables associated with source name
    :rtype: list
    """
    if product == "static":
        if comp_info.get("static") is None:
            raise ValueError(f"Product is set to static but no static sources/variables defined for {comp_info.get('type')}")

    ## Dictionary of variables associated with pp component source name
    ## are retrieved through Jinjafilter get_variables.py
    # 1. Loop through each element in dictionary passed
    # 2. match pp component source name with the requested source being assessed
    # 3. Save variables associated with that pp component
    for src_name in src_vars.keys():
        if req_source == src_name:
            v = src_vars[req_source]

    return v

def get_sources(comp_info: dict, product: str) -> List[str]:
    """
    Retrieve source name for a component

    :param comp_info: dictionary of information about requested component
    :type comp_info: dict
    :param product: static, ts, or av
    :type product: str
    :return: list of sources associated with a pp component
    :rtype: list
    """
    sources = []
    if "static" in product:
        for static_info in comp_info.get("static"):
            if static_info.get("source") is not None:
                sources.append(static_info.get("source"))
    else:
        for src_info in comp_info.get("sources"):
            sources.append(src_info.get("history_file"))

    return sources

def get_freq(comp_info: dict) -> List[str]:
    """
    Return the frequency

    :param comp_info: dictionary of information about requested component
    :type comp_info: dict
    :return: list of frequencies
    :rtype: list
    """
    if "freq" not in comp_info.keys():
        freq = glob.glob("*")
    else:
        freq = comp_info.get("freq")

    return freq

def get_chunk(comp_info: dict) -> List[str]:
    """
    Return the chunk size

    :param comp_info: dictionary of information about requested component
    :type comp_info: dict
    :return: list of chunk sizes
    :rtype: list 
    """
    if "chunk" not in comp_info.keys():
        chunk = glob.glob("*")
    else:
        chunk = comp_info.get("chunk")

    return chunk

def remap_pp_components(input_dir: str, output_dir: str, begin_date: str, current_chunk: str,
                        product: str, component: str, copy_tool: str, yaml_config: str,
                        ts_workaround: bool, ens_mem: str):
    """
    Remap netcdf files to an updated output directory structure

    :param input_dir: input directory
    :type input_dir: str
    :param output_dir: output directory
    :type output_dir: str
    :param begin: date to begin post-processing
    :type begin: ISO string format
    :param current_chunk: current chunk to post-process
    :type current_chunk: str
    :param component: component that will be post-processed
    :type component: str
    :param product: variable to define time series or time averaging
    :type product: str
    :param ts_workaround: time series workaround
    :type ts_workaround: boolean
    :param ens_mem: ensemble member number
    :type ens_mem: str
    :param copy_tool: tool to use for copying files
    :type copy_tool: str
    :param yaml_config: yaml configuration file
    :type yaml_config: str
    :raises ValueError:
        - if no input files are found
        - if no offline diagnostic file is found
    """

    # List variables
    fre_logger.info("Arguments:")
    fre_logger.info("    input dir: %s", input_dir)
    fre_logger.info("    output dir: %s", output_dir)
    fre_logger.info("    begin: %s", begin_date)
    fre_logger.info("    current chunk: %s", current_chunk)
    fre_logger.info("    component: %s", component)
    fre_logger.info("    product: %s", product)
    fre_logger.info("    copy tool: %s", copy_tool)
    fre_logger.info("    yaml config: %s", yaml_config)
    fre_logger.info("    dirTSWorkaround: %s", ts_workaround)

    if not ens_mem:  ## if ens_mem is an empty string
        ens_mem = None
        fre_logger.info("    ens_mem: None")
    else:
        fre_logger.info("    ens_mem: %s", ens_mem)

    # Path to yaml configuration
    exp_dir = Path(__file__).resolve().parents[3]
    path_to_yamlconfig = os.path.join(exp_dir, yaml_config)
    # Load and read yaml configuration
    with open(path_to_yamlconfig,'r') as yml:
        yml_info = yaml.safe_load(yml)

    # Verify the input and output directories
    verify_dirs(input_dir, output_dir)

    # Start in input directory)
    with helpers.change_directory(input_dir):
        # Save dictionary of variables associated with each post=processed component
        src_vars_dict = helpers.get_variables(yml_info, component)

        comp = component.strip('""')
        # Make sure component/source is in the yaml configuration file
        for comp_info in yml_info["postprocess"]["components"]:
            yaml_components = comp_info.get("type")

            # Check that pp_components defined matches those in the yaml file
            fre_logger.debug("Is %s in %s?", comp, yaml_components)
            if comp in yaml_components:
                fre_logger.info("Component %s found in yaml config!", comp)
            else:
                continue

            # Continue if not looking at correct information for requested component
            if comp != comp_info.get("type"):
                fre_logger.warning("Info not associated with component, %s, requested", comp)
                continue

            offline_srcs=[]
            #if static but no static defined, skip
            if product == "static":
                if comp_info.get("static") is None:
                    fre_logger.warning('Product set to "static" but no static source requested defined')
                    continue

                # Save list of offline sources (if defined) for later
                for static_info in comp_info.get("static"):
                    if static_info.get("offline_source") is None:
                        continue

                    offline_srcs.append(static_info.get("offline_source"))

            ## Loop through grid
            # Set grid type if component has xyInterp defined or not
            grid = []
            if "xyInterp" not in comp_info.keys():
                grid.append("native")
            else:
                interp = comp_info.get("xyInterp").split(",")
                interp = '_'.join(interp)
                interp_method = comp_info.get("interpMethod")
                grid.append(f"regrid-xy/{interp}.{interp_method}")

            for g in grid:
                if ens_mem is not None:
                    newdir = f"{input_dir}/{g}/{ens_mem}"
                    os.chdir(newdir)
                else:
                    os.chdir(f"{input_dir}/{g}")

                ## Loop through sources
                sources = get_sources(comp_info, product)
                for s in sources:
                    if ens_mem is not None:
                        source_dir = os.path.join(input_dir, g, ens_mem, s)
                    else:
                        source_dir = os.path.join(input_dir, g, s)
                    if not os.path.exists(source_dir) and product == "av":
                        fre_logger.info("Source directory '%s' does not exist, "
                                        "but this could be expected, so skipping.",
                                         source_dir)
                        continue
                    os.chdir(source_dir)

                    ## Loop through freq
                    freq = get_freq(comp_info) ###might have to be a list

                    for f in freq:
                        if ens_mem is not None:
                            os.chdir(f"{input_dir}/{g}/{ens_mem}/{s}/{f}")
                        else:
                            os.chdir(f"{input_dir}/{g}/{s}/{f}")

                        ## Loop through chunk
                        chunk = get_chunk(comp_info)  ## might have to be a list ...
                        for c in chunk:
                            if c != current_chunk:
                                continue
                            if ens_mem is not None:
                                os.chdir(f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}")
                            else:
                                os.chdir(f"{input_dir}/{g}/{s}/{f}/{c}")

                            # Create directory
                            # ts output is written to final location, av is not.
                            # so convert the ts only to bronx-style
                            if product == "ts":
                                dirs = create_dir(out_dir = output_dir,
                                                  comp = comp,
                                                  freq = freq_to_legacy(f),
                                                  chunk = chunk_to_legacy(c),
                                                  ens = ens_mem,
                                                  dir_ts = ts_workaround)
                            else:
                                dirs = create_dir(out_dir = output_dir,
                                                  comp = comp,
                                                  freq = f,
                                                  chunk = c,
                                                  ens = ens_mem,
                                                  dir_ts = ts_workaround)

                            fre_logger.info("directory created: %s", dirs)

                            # Search for files in chunk directory
                            if ens_mem is not None:
                                os.chdir(f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}")
                            else:
                                os.chdir(f"{input_dir}/{g}/{s}/{f}/{c}")

                            ## VARIABLE INFORMATION for requested source
                            # Note: variable filtering not done for offline static diagnostics
                            v = get_varlist(comp_info, product, s, src_vars_dict)

                            files = search_files(product = product,
                                                 var = v,
                                                 source = s,
                                                 freq = f,
                                                 current_chunk = current_chunk,
                                                 begin = begin_date)

                            fre_logger.info("%d files found for component '%s', "
                                            "source '%s', "
                                            "product '%s', "
                                            "grid '%s', "
                                            "chunk '%s', "
                                            "variables '%s': %s",
                                            len(files), comp, s, product, g, c, v, files)

                            if not files:
                                if ens_mem is not None:
                                    raise ValueError("\nError: No input files found in",
                                                     f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}")
                                else:
                                    raise ValueError("\nError: No input files found in",
                                                     f"{input_dir}/{g}/{s}/{f}/{c}")

                            os.chdir(output_dir)

                            for file in files:
                                newfile1 = file.split(".",1)[1]
                                newfile2 = f"{comp}.{newfile1}"
                                # If file exists, remove it
                                # (would exist if workflow was run previously)
                                output_file = os.path.join(output_dir, dirs, newfile2)
                                if os.path.exists(output_file):
                                    os.remove(output_file)
                                fre_logger.info("NEWFILE2: %s", newfile2)
                                # Symlink or copy the file for the specified
                                # component in the output directory
                                if ens_mem is not None:
                                    link = ["ln",
                                            f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}/{file}",
                                            f"{output_dir}/{dirs}/{newfile2}"]
                                else:
                                    link = ["ln",
                                            f"{input_dir}/{g}/{s}/{f}/{c}/{file}",
                                            f"{output_dir}/{dirs}/{newfile2}"]

                                run = subprocess.run( link, check = False )
                                ret = run.returncode

                                if ret != 0:
                                    if ens_mem is None:
                                        copy = [f"{copy_tool}",
                                                f"{input_dir}/{g}/{s}/{f}/{c}/{file}",
                                                f"{output_dir}/{dirs}/{newfile2}" ]
                                        subprocess.run( copy, check = False )
                                    else:
                                        copy = [f"{copy_tool}",
                                                f"{input_dir}/{g}/{ens_mem}/{s}/{f}/{c}/{file}",
                                                f"{output_dir}/{dirs}/{newfile2}" ]
                                        subprocess.run( copy, check = False )

                            # Symlink or copy the offline diagnostic file for the
                            # specified component in the output directory.
                            # Offline diagnostic files will then be in the same
                            # location as other static files to be combined.
                            if offline_srcs is not None:
                                for src_file in offline_srcs:
                                    if not Path(src_file).exists():
                                        raise ValueError("Offline diagnostic file defined but "
                                                         f"{src_file} does not exist or cannot "
                                                         "be found!")

                                    offline_link = ["ln",
                                                    "-s",
                                                    f"{src_file}",
                                                    f"{output_dir}/{dirs}"]
                                    offline_link_run = subprocess.run( offline_link, check = False )
                                    offline_link_ret = offline_link_run.returncode

                                    if offline_link_ret != 0:
                                        #raise ValueError("copy failed")
                                        offline_copy = ["{copy_tool}",
                                                        f"{src_file}",
                                                        f"{output_dir}/{dirs}"]
                                        subprocess.run( offline_copy, check = False )

    fre_logger.info("Component remapping complete")
