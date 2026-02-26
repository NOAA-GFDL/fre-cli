import json


class AnalysisScript(object):
    """Abstract base class for analysis scripts.  User-defined analysis scripts
       should inhert from this class and override the requires and run_analysis methods.

    Attributes:
       description: Longer form description for the analysis.
       title: Title that describes the analysis.
    """
    def __init__(self):
        """Instantiates an object.  The user should provide a description and title."""
        raise NotImplementedError("you must override this function.")
        self.description = None
        self.title = None

    def requires(self):
        """Provides metadata describing what is needed for this analysis to run.

        Returns:
            A json string describing the metadata.
        """
        raise NotImplementedError("you must override this function.")
        return json.dumps("{json of metadata MDTF format.}")

    def run_analysis(self, yaml, name, date_range, scripts_dir, output_dir, output_yaml):
        """Runs the analysis and generates all plots and associated datasets.

        Args:
            yaml: Path to a model yaml
            name: Name of the analysis as specified in the yaml
            date_range: Time span to use for analysis (YYYY-MM-DD,YYYY-MM-DD)
            scripts_dir: Path to a directory to save intermediate scripts
            output_dir: Path to a directory to save figures
            output_yaml: Path to use as an structured output yaml file

        Returns:
            A list of png figures.
        """
        raise NotImplementedError("you must override this function.")
        return ["figure1.png", "figure2.png",]
