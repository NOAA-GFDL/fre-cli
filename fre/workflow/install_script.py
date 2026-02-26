''' fre workflow install '''
from pathlib import Path
import subprocess
import logging
from fre.app.helpers import change_directory

fre_logger =logging.getLogger(__name__)

def workflow_install(experiment: str, src_dir: str, target_dir: str, force_install: bool):
    """
    Install the Cylc workflow definition located in
    cylc-src/$(experiment) to cylc-run/$(experiment)

    :param experiment: Experiment names from the yaml displayed by
                       fre list exps -y $yamlfile (e.g. c96L65_am5f4b4r0_amip);
                       default None
    :type experiment: str
    :param src_dir: src_dir/workflow_name
    :type src_dir:
    :param target_dir:
    :type target_dir:
    """
    workflow_name = experiment

    # Check src_dir exists
    if not Path(src_dir):
        raise ValueError("""Cylc source directory ({src_dir}) could not be found! Try specifying
                            path by passing --src-dir [path].""")

    # if the cylc-run directory already exists,
    # then check whether the cylc expanded definition (cylc config)
    # is identical. If the same, good. If not, bad.
    install_dir = Path(f"{target_dir}/cylc-run")
    if Path(install_dir).is_dir():
        fre_logger.warning(" *** PREVIOUS INSTALL FOUND: %s ***", install_dir)
        if force_install:
            fre_logger.warning(" *** REMOVING %s *** ", install_dir)
            install_output = subprocess.run(["cylc", "clean", f"{install_dir}/{workflow_name}"],
                                            capture_output = True,
                                            text = True,
                                            check = True)
            fre_logger.debug(install_output)
        else:
            # must convert from bytes to string for proper comparison
            installed_def = subprocess.run(["cylc", "config", workflow_name],
                                           capture_output=True,
                                           check=True).stdout.decode('utf-8')
            with change_directory(src_dir):
                source_def = subprocess.run(['cylc', 'config', '.'],
                                            capture_output=True,
                                            check=True).stdout.decode('utf-8')

            if installed_def == source_def:
                fre_logger.warning("""NOTE: Workflow '%s/%s}' already ",
                                      installed, and the definition is unchanged""", install_dir, workflow_name)
            else:
                fre_logger.error("ERROR: Please remove installed workflow with one of these options:")
                fre_logger.error("  - fre workflow install -e %s --src-dir %s --target-dir %s --force-install", experiment, src_dir, target_dir)
                fre_logger.error("  - cylc clean %s/%s, then re-run install command", install_dir, workflow_name)
                raise ValueError(f"""ERROR: Workflow '{install_dir}/{workflow_name}' already
                                     installed, and the definition has changed!""")

    if not Path(install_dir).is_dir():
        fre_logger.warning("NOTE: About to install workflow into ~/cylc-run/%s", workflow_name)
        if not target_dir:
            # install workflow in default home location
            cmd = f"cylc install --no-run-name {src_dir}"
            subprocess.run(cmd, shell=True, check=True)
        else:
            # symlink the workflow and associated files in target_dir
            cmd = f"cylc install --no-run-name {src_dir} --symlink-dirs='{target_dir}/{workflow_name}'"
            subprocess.run(cmd, shell=True, check=True)
