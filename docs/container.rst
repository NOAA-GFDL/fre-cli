FRE-cli Container (For post-procesing use case)
=========================

Previously, many GFDL workflows and configurations have only been accessible on gitlab. This is disadvantageous for outside collaboration, flexibility, community development. While the FRE workflow can now be conda installed, another deployment method of containerization has been developed. Containerzation of the FRE-cli subtools at GFDL bolsters portability while also simplifying the environment set-up for the user. With the environment set-up done through the container build, this FRE-cli container work allows for more effective sharing of the subtools.

BUILDING
--------

In order to build the container, the user needs to have podman access on Gaea. If needed, submit a servicedesk ticket.

Files used to build container:
    - Dockerfile-fre-cli
    - cylc-flow-tools.yaml (environment yaml)
    - runscript.sh

The container will house the fre-cli tools and any necessary packages needed for those tools.

Using podman and apptainer to build, follow these steps:

1. Navigate to `/tmp/containers/$USER` (create if needed)

.. code-block:: console

 mkdir /tmp/containers/$USER
 cd /tmp/containers/$USER

1. Clone the FRE-cli repository

.. code-block:: console

 git clone https://github.com/NOAA-GFDL/fre-cli.git
 cd fre-cli

2. Build the container image

.. code-block:: console

 podman build -f container-files/Dockerfile-fre-cli -t 2026.01

3. Save the image to a local tar file

.. code-block:: console

 podman save -o [name of container].tar localhost/2026.01

4. Create the singularity image file (sif) from the tar file

.. code-block:: console

 apptainer build --disable-cache [name of container].sif docker-archive://[name of container].tar

SETUP
-----

Now that the FRE workflows container is created, certain files and directories must be made accessible.

**Repos and Configuration files**

In order to run the post-processing workflow, certain repositories and files are needed:

- Directory that will include folders and files for container set-up and output (could be named ppp-setup for example)
    - Create an empty ppp-setup folder in an area with ample space as this is where the post-processing run output will be populated.
    - This setup/output directory consists of a few subdirectories, pp, ptmp, and temp, that will be created through the runscript.sh script found in the container (`/app/exec/runscript.sh`)

- Yaml configuration files
    - Publicly available example yaml configuration files can be found `here, in fre-examples <https://github.com/NOAA-GFDL/fre-examples>`_

**Data files**

Additionally, history files and grid spec files are needed.

*If on Gaea*, history files and grid spec files are usually available in a certain location; retrieve their locations
    - Paths to the history folder and grid spec file will be mounted as read only folders/files when running the container

*If not on Gaea*, history file and grid spec data should be transferred to the "ppp-setup" location:
    - ppp-setup/history/
    - ppp-setup/[experiment]_grid/

FOR CLOUD USERS: Preparing for cloud usage requires history files and container image/runscript to be transferred to the cloud resource. The recommended method of file transfer is with Globus.

Refer to globus documentation here: `Globus Online Data Transfer <https://docs.rdhpcs.noaa.gov/data/globus_online_data_transfer.html>`_

**YAML Configuration Edits**

Regarding the yaml configurations, since some paths/data will be mounted into the container for the post-processing run, we need to be edit those paths to reference where the folder would be located INSIDE the container. These include:
    - &GRID_SPEC96 "/mnt/[experimentname]_grid/[gridSpec file]
    - history_dir: "/mnt/history"
    - pp_dir: "/mnt/pp"
    - ptmp_dir: "/mnt/ptmp"

RUNNING
-------
To run the container, follow these steps:

1. Use apptainer or singularity to run
2. Make sure container folders are writable
3. Bind in necessary locations (empty setup/output folder, data locations)
4. Run:

.. code-block:: console

   apptainer exec --writable-tmpfs --bind [Path/to/setup/folder]:/mnt --bind [Path/to/gridspec location]:/mnt/[experiment-name]_grid:ro --bind [Path/to/history/files]:/mnt/history:ro [Path/to/created/container] /app/exec/runscript.sh

NOTE: It is essential that binding is done correctly as the container’s runscript (for post-processing) relies heavily on these paths.

Here,
    - `--writable-tmpfs` allows files in the container to be editable, but temporarily (as long as the container is running)
    - `--bind` mounts the listed folders/files into the corresponding location in the container
    - ro refers to read-only, so that data files are not corrupted in any way.
    - At this point, the container’s runscript will begin to run. User input is required, listing the experiment, platform, target, and post-processing yaml file.

The post-processing experiment will be installed, configuration files will be validated, and the experiment should kick off.

REVIEW
------

The setup-output directory created earlier will hold pp output for review. It will also hold a newly created cylc-run directory.
