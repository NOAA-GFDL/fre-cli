""" Workflow checkout """
import os
import subprocess
from pathlib import Path
import logging
import shutil
import json
from jsonschema import validate, SchemaError, ValidationError
from typing import Optional

import fre.yamltools.combine_yamls_script as cy
from fre.app.helpers import change_directory

fre_logger = logging.getLogger(__name__)

######VALIDATE#####
def validate_yaml(yamlfile: dict, application: str):
    """
    Validate the format of the yaml file against the
    schema.json held in [gfdl_msd_schemas](https://github.com/NOAA-GFDL/gfdl_msd_schemas).

    :param yamlfile: Dictionary containing the combined model,
                     settings, pp, and analysis yaml content
    :type yamlfile: dict
    :param application: type of workflow to check out/clone 
    :type application: string
    :raises ValueError:
        - invalid gfdl_msd_schema path
        - invalid combined yaml
        - unclear error in validation
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
        fre_logger.info(" ** COMBINED YAML VALID ** ")
    except SchemaError as exc:
        raise ValueError(f"Schema '{schema_path}' is not valid. Contact the FRE team.") from exc
    except ValidationError as exc:
        raise ValueError("Combined yaml is not valid. Please fix the errors and try again.") from exc
    except Exception as exc:
        raise ValueError("Unclear error from validation. Please try to find the error and try again.") from exc

def workflow_checkout(target_dir: str, yamlfile: str = None, experiment: str = None, application: str = None, force_checkout: Optional[bool] = False):
    """
    Create a directory and clone the workflow template files from a specified repository.

    :param yamlfile: Model yaml configuration file
    :type yamlfile: str
    :param experiment: One of the experiment names listed in the model yaml file.
                       Note: the command "fre list exps -y [model_yamlfile]" can be used to
                       list the available experiment names
    :type experiment: str
    :param application: String used to specify the type of workflow to be used/cloned.
                        Ex.: run, postprocess
    :type application: str
    :param target_dir: Target location to create the cylc-src/<workflow> directory in
    :type target_dir: str
    :param force_checkout: re-clone the workflow repository if it exists
    :type force_checkout: bool
    :raises OSError: if the checkout script cannot be created
    :raises ValueError:
        - if the repository and/or tag was not defined
        - if the target directory does not exist or cannot be found
        - if tag or branch does not match the git clone branch arg
    """
    # Used in consolidate_yamls function for now
    platform = None
    target = None

    if application in ["run", "pp"]:
        fre_logger.info(" ** Configuring the resolved YAML for the %s **", application)
        yaml = cy.consolidate_yamls(yamlfile=yamlfile,
                                    experiment=experiment,
                                    platform=platform,
                                    target=target,
                                    use=application,
                                    output="config.yaml")

        validate_yaml(yamlfile = yaml, application = application)

        # Reset application for pp to make it discoverable in yaml config
        if application == "pp":
            application = "postprocess"

        workflow_info = yaml.get(application).get("workflow")

    repo = workflow_info.get("repository")
    tag = workflow_info.get("version")
    fre_logger.info("Defined tag ==> '%s'", tag)

    if None in [repo, tag]:
        raise ValueError(f"One of these are None: repo / tag = {repo} / {tag}")

    fre_logger.info("(%s):(%s) check out for %s ==> REQUESTED", repo, tag, application)

    # Create src_dir if it does not exist
    if not Path(target_dir).exists():
        Path(target_dir).mkdir(parents=True, exist_ok=True)

    # Define cylc-src directory
    src_dir = f"{target_dir}/cylc-src"
    # workflow name
    workflow_name = experiment

    # create workflow in cylc-src
    try:
        Path(src_dir).mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        raise OSError(
            f"(checkoutScript) directory {src_dir} wasn't able to be created. exit!") from exc

    if Path(f"{src_dir}/{workflow_name}").is_dir():
        fre_logger.info(" *** PREVIOUS CHECKOUT FOUND: %s/%s *** ", src_dir, workflow_name)
        if force_checkout:
            fre_logger.warning(" *** REMOVING %s/%s *** ", src_dir, workflow_name)
            shutil.rmtree(f"{src_dir}/{workflow_name}")
        else:
            with change_directory(f"{src_dir}/{workflow_name}"):
                # capture the branch and tag
                # if either match git_clone_branch_arg, then success. otherwise, fail.
                current_tag = subprocess.run(["git","describe","--tags"],
                                             capture_output = True,
                                             text = True, check = True).stdout.strip()
                current_branch = subprocess.run(["git", "branch", "--show-current"],
                                                 capture_output = True,
                                                 text = True, check = True).stdout.strip()

                if tag in (current_tag, current_branch):
                    fre_logger.warning("Checkout exists ('%s/%s'), and matches '%s'", src_dir, workflow_name, tag)
                else:
                    fre_logger.error(
                        "ERROR: Checkout exists ('%s/%s') and does not match '%s'", src_dir, workflow_name, tag)
                    fre_logger.error(
                        "ERROR: Current branch: '%s', Current tag-describe: '%s'", current_branch, current_tag)
                    raise ValueError('Neither tag nor branch matches the git clone branch arg')
    if not Path(f"{src_dir}/{workflow_name}").is_dir():
        fre_logger.info("Workflow does not exist; will create now")
        clone_output = subprocess.run( ["git", "clone","--recursive",
                                        f"--branch={tag}",
                                        repo, f"{src_dir}/{workflow_name}"],
                                        capture_output = True, text = True, check = True)
        fre_logger.debug(clone_output)
        fre_logger.info("(%s):(%s) check out ==> SUCCESSFUL", repo, tag)

        ## Move combined yaml to cylc-src location
        current_dir = Path.cwd()
        shutil.move(Path(f"{current_dir}/config.yaml"), f"{src_dir}/{workflow_name}")
        fre_logger.info("Combined yaml file moved to %s/%s", src_dir, workflow_name)
