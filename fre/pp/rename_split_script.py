import logging
from pathlib import Path
import xarray as xr

fre_logger = logging.getLogger(__name__)

def rename_split_script(input_dir: str, output_dir: str, component: str, use_subdirs: bool):
    """
    Accept a flat directory of NetCDF files and output a nested directory structure
    containing frequency and time interval.
    If hard-linking is available, use it; otherwise copy.
    For regridded cases, accept subdirectories corresponding to the regrid label
    in the input directory and use them in the output directory.
    """
    input_dir = Path(input_dir)
    if use_subdirs:
        fre_logger.info("Using subdirs")
        subdirs = [x for x in input_dir.iterdir() if x.is_dir()]
        for subdir in subdirs:
            print("woo", subdir)
    else:
        fre_logger.info("Not using subdirs")
        print("woo2", input_dir)
        files = input_dir.glob(f"*.{component}.*")
        for file in files:
            print("its a file", file)
            parts = file.stem.split('.')
            print("ha", len(parts))
            print(parts)
            if len(parts) == 4:
                date = parts[0]
                label = parts[1]
                tile = parts[2]
                var = parts[3]
            elif len(parts) == 3:
                date = parts[0]
                label = parts[1]
                var = parts[2]
            else:
                raise Exception(f"File '{file}' cannot be parsed")
            # open the nc file
            ds = xr.open_dataset(file)
            number_of_timesteps = ds.sizes['time']
            print("ok", number_of_timesteps)
