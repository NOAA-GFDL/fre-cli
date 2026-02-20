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
    Validate the format of the yaml file based
    on the schema.json in gfdl_msd_schemas

    :param yamlfile: Model, settings, pp, and analysis yaml
                     information combined into a dictionary
    :type yamlfile: dict
    :param application: type of workflow to check out/clone 
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

def create_checkout(repo: str, tag: str, src_dir: str, workflow_name: str):
    """
    Clone the workflow template files from a defined repo into the cylc-src/workflow
    directory and move the resolved yaml to the cylc-src directory.

    :param repo: Yaml defined workflow repository
    :type repo: str
    :param tag: branch or version of defined repository 
    :type tag: str
    :param src_dir: Cylc-src directory 
    :type src_dir: str
    :param workflow_name: Name of workflow
    :type workflow_name: src
    """
    # scenarios 1+2, checkout doesn't exist, branch specified (or not)
    clone_output = subprocess.run( ["git", "clone","--recursive",
                                    f"--branch={tag}",
                                    repo, f"{src_dir}/{workflow_name}"],
                                    capture_output = True, text = True, check = True)
    fre_logger.debug(clone_output)
    fre_logger.warning("(%s):(%s) check out ==> SUCCESSFUL", repo, tag)

    ## Move combined yaml to cylc-src location
    current_dir = Path.cwd()
    shutil.move(Path(f"{current_dir}/config.yaml"), f"{src_dir}/{workflow_name}")
    fre_logger.info("Combined yaml file moved to %s/%s", src_dir, workflow_name)

def workflow_checkout(target_dir: str, yamlfile: str = None, experiment: str = None, application: str = None, force_checkout: Optional[bool] = False):
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
    :param target_dir: Target directory to clone repository into
    :type target_dir: str
    :param force_checkout: re-clone the workflow repo if it exists
    :type force_checkout: bool
    :raises OSError: if the checkout script was not able to be created
    :raises ValueError:
        - if the repo and/or tag was not defined
        - if the target directory does not exist or cannot be found
        - if the 
                raise ValueError('Neither tag nor branch matches the git clone branch arg')

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
        workflow_info = yaml.get("workflow").get("run")
    elif application == "pp":
        # will probably be taken out and put above is "use"
        # is generalized in this tool
        yaml = cy.consolidate_yamls(yamlfile=yamlfile,
                                    experiment=experiment,
                                    platform=platform,
                                    target=target,
                                    use="pp",
                                    output="config.yaml")
        #validate_yaml(yamlfile = yaml, application = "pp")
        workflow_info = yaml.get("workflow").get("pp")

    repo = workflow_info.get("repo")
    tag = workflow_info.get("version")
    fre_logger.info("Defined tag ==> '%s'", tag)

    if None in [repo, tag]:
        raise ValueError(f"One of these are None: repo / tag = {repo} / {tag}")

    fre_logger.warning("(%s):(%s) check out ==> REQUESTED", repo, tag)

    # Make sure src_dir exists
    if not Path(target_dir).exists():
        raise ValueError(f"Target directory {target_dir} does not exist or cannot be found.")

    # clone directory
    src_dir = f"{target_dir}/cylc-src"
    # workflow name
    workflow_name = experiment

    # create workflow in cylc-src
    try:
        Path(src_dir).mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        raise OSError(
            f"(checkoutScript) directory {src_dir} wasn't able to be created. exit!") from exc

    if not Path(f"{src_dir}/{workflow_name}").is_dir():
        fre_logger.info("Workflow does not yet exist; will create now")
        create_checkout(repo = repo,
                        tag = tag,
                        src_dir = src_dir,
                        workflow_name = workflow_name)
    elif Path(f"{src_dir}/{workflow_name}").is_dir() and force_checkout:
        fre_logger.warning(" *** PREVIOUS CHECKOUT FOUND: %s/%s *** ", src_dir, workflow_name)
        # Remove checked out repo
        shutil.rmtree(f"{src_dir}/{workflow_name}")
        fre_logger.warning(" *** REMOVING %s/%s *** ", src_dir, workflow_name)
        # Redo checkout
        create_checkout(repo = repo,
                        tag = tag,
                        src_dir = src_dir,
                        workflow_name = workflow_name)
    elif Path(f"{src_dir}/{workflow_name}").is_dir() and not force_checkout:
        fre_logger.warning(" *** PREVIOUS CHECKOUT FOUND: %s/%s *** ", src_dir, workflow_name)
        # the repo checkout does exist, scenarios 3 and 4.
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
