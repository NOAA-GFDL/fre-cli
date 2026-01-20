import logging
from pathlib import Path, PurePosixPath
import requests
from ..base_class import AnalysisScript
import esnb.engine

fre_logger = logging.getLogger(__name__)

class freanalysis_esnb(AnalysisScript):
    """Defines run and report-requirements methods for ESNB flavor usage
    """

    def __init__(self):
        self.description = "Wrapper to access analysis framework for ESNB scripts"
        self.title = "ESNB"

    def run_analysis(self, config, name, date_range, scripts_dir, output_dir, output_yaml, pp_dir):
        """Runs the ESNB analysis specified in the yaml and the runtime options

        Args:
            config: Dictionary of specific configuration for the script
            name: Name of the analysis as specified in the yaml
            date_range: Time span to use for analysis (YYYY-MM-DD,YYYY-MM-DD)
            scripts_dir: Path to a directory to save intermediate scripts
            output_dir: Path to a directory to save figures
            output_yaml: Path to use as an structured output yaml file
            pp_dir: Path to input postprocessed files
        """

        # save notebook to scripts_dir
        url = config["notebook_path"]
        # convert to the "Raw" URL
        # replace 'github.com' with 'raw.githubusercontent.com' and remove '/blob'
        raw_url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
        local_filename = Path(scripts_dir) / PurePosixPath(url).name
        with requests.get(raw_url) as r:
            r.raise_for_status() # Check for HTTP errors (404, 500, etc.)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        fre_logger.debug(f"ESNB notebook saved to '{local_filename}'")

        # create run_settings dictionary
        run_settings = {
            'conda_env_root': config["conda_env_root"],
            'notebook_path': local_filename,
            'outdir': output_dir,
            'scripts_dir': scripts_dir
        }

        # create case_settings dictionary
        split_date = date_range.split(",")
        case_settings = {
            'PP_DIR': pp_dir,
            'date_range': split_date
        }

        # write the python script that runs the notebook
        python_script = esnb.engine.canopy_launcher(run_settings, case_settings, verbose=True)
        fre_logger.debug(f"ESNB python wrapper saved to '{python_script}'")

        # run the python script

