Post-Processing Container
=========================

The FRE post-processing container packages fre-cli and its dependencies into a portable
Apptainer/Singularity image, enabling postprocessing on systems where a full conda install is
not practical. The container is distributed as a pre-built ``.sif`` file.

SETUP
-----

Now that the FRE workflows container is created, certain files and directories must be made accessible.

**Repos and Configuration files**

In order to run the post-processing workflow, certain repositories and files are needed:

1. fre-workflows cloned repository
    - Can be found `here, in fre-workflows <https://github.com/NOAA-GFDL/fre-workflows>`_

2. Directory that will include folders and files for container set-up and running (could be named ppp-setup for example)
    - The setup/output directory consists of a few subdirectories: pp, ptmp, and temp (these are created through the runscript.sh in this repository for the container)
    - Ensure you create the empty ppp-setup folder in an area with enough space as this is where the post-processing run output will be populated.

3. Yaml configuration files
    - Publicly available example yaml configuration files can be found `here, in fre-examples <https://github.com/NOAA-GFDL/fre-examples>`_

**Data files**

Additionally, history files and grid spec files are needed.

*If on Gaea*, history files and grid spec files are usually available in a certain location; retrieve their locations
    - Paths to the history folder and grid spec file will be mounted into the container as read only folders/files

*If not on Gaea*, history file and grid spec data should be transferred to the ppp-setup location in:
    - ppp-setup/history/
    - ppp-setup/[experiment]_grid/

FOR CLOUD USERS: Preparing for cloud usage requires history files and container image/runscript to be transferred to the cloud resource. The recommended method of file transfer is with Globus in which files should be transferred to the cloud resource’s lustre folder.

Refer to globus documentation here: `Globus Online Data Transfer <https://docs.rdhpcs.noaa.gov/data/globus_online_data_transfer.html>`_

**Configuration Edits**

Regarding the yaml configurations, some paths need to be edited to reference the file location mounted inside the container. These include:
    - &GRID_SPEC96 "/mnt/[experimentname]_grid/[gridSpec file]
    - history_dir: "/mnt/history"
    - pp_dir: "/mnt/pp"
    - ptmp_dir: "/mnt/ptmp"

RUNNING
-------
To run the container, follow these steps:

1. Use apptainer or singularity to run
2. Make sure directories are writable
3. Bind in necessary locations (setup folder, workflow folder, data locations)
4. Run:

.. code-block:: console

   apptainer exec --writable-tmpfs --bind [Path/to/setup/folder]:/mnt --bind [Path/to/fre-workflows]:/mnt2 --bind [Path/to/gridspec location]:/mnt/[experiment-name]_grid:ro --bind [Path/to/history/files]:/mnt/history:ro [Path/to/created/container] /app/exec/runscript.sh

NOTE: It is essential that binding is done correctly as the container’s runscript relies heavily on these paths.

Here,
    - --writable-tmpfs allows files in the container to be editable, but temporarily (as long as the container is running)
    - --bind mounts that
    - ro refers to read-only, so that data files are not corrupted in any way.
    - At this point, the container’s runscript will begin to run. User input is required, listing the experiment, platform, target, and post-processing yaml file.

The experiment will be installed, configuration files will be validated, and the experiment should kick off.

REVIEW
------

The setup-output directory created earlier will hold pp output for review. It will also hold a newly created cylc-run directory.
