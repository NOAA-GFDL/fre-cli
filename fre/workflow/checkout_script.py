""" Workflow checkout """
import os
import subprocess
from pathlib import Path
import logging
import shutil 

import fre.yamltools.combine_yamls_script as cy
from fre.app.helpers import change_directory
#from . import make_workflow_name
from jsonschema import validate, SchemaError, ValidationError

fre_logger = logging.getLogger(__name__)

FRE_PP_WORKFLOW = "https://github.com/NOAA-GFDL/fre-workflows.git"
FRE_RUN_WORKFLOW = "https://github.com/NOAA-GFDL/fre-workflows.git"

######VALIDATE#####
def validate_yaml(yamlfile: dict, application: str) -> None:
    """
    Validate the format of the yaml file based
    on the schema.json in gfdl_msd_schemas

    :param yamlfile: Model, settings, pp, and analysis yaml
                     information combined into a dictionary
    :type yamlfile: dict
    :param application: ------------------------------------------------
    :type application: string
    :raises ValueError:
        - if gfdl_mdf_schema path is not valid
        - combined yaml is not valid
        - unclear error in validation
    :return: None
    :rtype: None
    """
    schema_dir = Path(__file__).resolve().parents[1]
    schema_path = os.path.join(schema_dir, 'gfdl_msd_schemas', 'FRE', f'fre_{application}.json')
    fre_logger.info("Using yaml schema '%s'", schema_path)
    # Load the json schema: .load() (vs .loads()) reads and parses the json in one)
    try:
        with open(schema_path,'r', encoding='utf-8') as s:
            schema = json.load(s)
    except:
        fre_logger.error("Schema '%s' is not valid. Contact the FRE team.", schema_path)
        raise

    # Validate yaml
    # If the yaml is not valid, the schema validation will raise errors and exit
    try:
        validate(instance = yamlfile,schema=schema)
        fre_logger.info("Combined yaml valid")
    except SchemaError as exc:
        raise ValueError(f"Schema '{schema_path}' is not valid. Contact the FRE team.") from exc
    except ValidationError as exc:
        raise ValueError("Combined yaml is not valid. Please fix the errors and try again.") from exc
    except Exception as exc:
        raise ValueError("Unclear error from validation. Please try to find the error and try again.") from exc

def workflow_checkout(yamlfile: str = None, experiment = None, application = None):
    """
    Create a directory and clone the workflow template files from a defined repo.

    :param yamlfile: Model yaml configuration file
    :type yamlfile: str
    :param experiment: One of the postprocessing experiment names from the
                       yaml displayed by fre list exps -y $yamlfile 
                       (e.g. c96L65_am5f4b4r0_amip), default None
    :type experiment: str
    :param application: Which workflow will be used/cloned
    :type application: str
    :raises OSError: why checkout script was not able to be created
    :raises ValueError:
        -if experiment or platform or target is None
    """
    # Used in consolidate_yamls function for now
    platform = None
    target = None
    if application == "run":
        fre_logger.info("NOT DONE YET")
        # will probably be taken out and put above is "use"
        # is generalized in this tool
        yaml = cy.consolidate_yamls(yamlfile=yamlfile,
                                    experiment=experiment,
                                    platform=platform,
                                    target=target,
                                    use="run",
                                    output=None)
        #validate_yaml(yamlfile = yaml, application = "run")
        workflow_info = yaml.get("workflow").get("run_workflow")
    elif application == "pp":
        # will probably be taken out and put above is "use"
        # is generalized in this tool
        yaml = cy.consolidate_yamls(yamlfile=yamlfile,
                                    experiment=experiment,
                                    platform=platform,
                                    target=target,
                                    use="pp",
                                    output=f"config.yaml")
        #validate_yaml(yamlfile = yaml, application = "pp")
        workflow_info = yaml.get("workflow").get("pp_workflow")

    repo = workflow_info.get("repo")

    tag = workflow_info.get("version")
    fre_logger.info("Defined tag ==> '%s'", tag)

    if None in [repo, tag]:
        raise ValueError(f"One of these are None: repo / tag = {repo} / {tag}")

    fre_logger.warning("(%s):(%s) check out ==> REQUESTED", repo, tag)

    # clone directory
    directory = os.path.expanduser("~/cylc-src")
    # workflow name
    workflow_name = experiment

    # create workflow in cylc-src
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        raise OSError(
            f"(checkoutScript) directory {directory} wasn't able to be created. exit!") from exc

    if not Path(f"{directory}/{workflow_name}").is_dir():
        # scenarios 1+2, checkout doesn't exist, branch specified (or not)
        fre_logger.info("Workflow does not yet exist; will create now")
        clone_output = subprocess.run( ["git", "clone","--recursive",
                                        f"--branch={tag}",
                                        repo, f"{directory}/{workflow_name}"],
                                        capture_output = True, text = True, check = True)
        fre_logger.debug(clone_output)
        fre_logger.warning("(%s):(%s) check out ==> SUCCESSFUL", repo, tag)

        ## Move combined yaml to cylc-src location
        cylc_src_dir = os.path.join(os.path.expanduser("~/cylc-src"), f"{experiment}")
        current_dir = Path.cwd()
        shutil.move(Path(f"{current_dir}/config.yaml"), cylc_src_dir)
        fre_logger.info("Combined yaml file moved to ~/cylc-src/%s", experiment)
    else:
        # the repo checkout does exist, scenarios 3 and 4.
        with change_directory(f"{directory}/{workflow_name}"):
            # capture the branch and tag
            # if either match git_clone_branch_arg, then success. otherwise, fail.
            current_tag = subprocess.run(["git","describe","--tags"],
                                         capture_output = True,
                                         text = True, check = True).stdout.strip()
            current_branch = subprocess.run(["git", "branch", "--show-current"],
                                             capture_output = True,
                                             text = True, check = True).stdout.strip()

            if tag in (current_tag, current_branch):
                fre_logger.warning("Checkout exists ('%s/%s'), and matches '%s'", directory, workflow_name, tag)
            else:
                fre_logger.error(
                    "ERROR: Checkout exists ('%s/%s') and does not match '%s'", directory, workflow_name, tag)
                fre_logger.error(
                    "ERROR: Current branch: '%s', Current tag-describe: '%s'", current_branch, current_tag)
                raise ValueError('Neither tag nor branch matches the git clone branch arg')
