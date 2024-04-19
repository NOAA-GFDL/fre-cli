#!/usr/bin/env python
#frepp.py
#replacement for the frepp bash script located at: 
#https://gitlab.gfdl.noaa.gov/fre2/system-settings/-/blob/main/bin/frepp
#~/Code/fre-cli/fre/frepp/wrapperscript
#Author: Carolyn.Whitlock

#todo: 
# add relative path import to rest of pp tools
# add command-line args using same format as fre.py
# include arg for pp start / stop
# test yaml path
# error handling

import sys
import os
import subprocess
from subprocess import PIPE
from subprocess import STDOUT
import click
import re

# Import from the local packages
from .checkoutScript import _checkoutTemplate
from .configureScriptXML import _convert
from .configureScriptYAML import _yamlInfo
from .validate import _validate_subtool
from .install import _install_subtool
from .run import _pp_run_subtool 
from .status import _status_subtool 

def runFre2pp(config_file, experiment, platform, target, branch="main", time=0000):
    '''
    Wrapper script for calling a FRE2 pp experiment with the canopy-style
    infrastructure and fre-cli
    '''
    
    #dumb xml check;does it need to be smarter?
    is_xml = (config_file[-3:] == "xml")

    #env_setup
    try:
        _checkoutTemplate(experiment, platform, target, branch)
    except Exception as err:
        raise
    
    if is_xml:
        #TODO: should this prompt for pp start/stop years?
        try:
            _convert(config_file, platform, target, experiment, do_analysis=False)
            #note: arg list for this function is a looooot longer, but all those
            #args can be deduced from the xml when given default vals
        except Exception as err:
            raise
        try:
            _validate_subtool(experiment, platform, target)
            #See notes in main() function
        except Exception as err:
            raise
    else:
        try:
            _yamlInfo(config_file, experiment, platform, target)
        except Exception as err:
            raise
    
    try:
        _install_subtool(experiment, platform, target)
    except:
        raise        
    
    try:
        _pp_run_subtool(experiment, platform, target)
    except Exception as err:
        raise    
    
    #send off a watcher script that reports on how it's going
    for n in range(1,12):
        try:
            _status_subtool()
        except Exception as err:
            raise
        time.sleep(300)

#############################################


def print_run_error():
    '''
    run_error text from prior wrapperscript (frepp)
    '''
    run_error = '''    
################################################################################
Unfortunately, there are failed tasks, probably caused by refineDiag errors
or try to use a history file that does not exist.

While Cylc workflows can be configured to handle failure gracefully,
this workflow is not yet set to do this, so currently it's recommended
to reconfigure your postprocessing to remove task errors.

For some suggestions to recover from the above most common errors, see:

frepp --help
################################################################################
'''
    print(run_error)
    
def print_validation_error():
    '''
    validate_error text from prior wrapperscript (frepp)
    '''
    validate_error = '''
################################################################################
Configuration may not be valid.

In general, Canopy configurations should pass all available validation scripts.
To run them,

cd $HOME/cylc-src/$name
rose macro --validate

Most validation errors reflect configurations problems that should be corrected.
The exceptions are:
1. PP_DIR will be created if it does not exist
2. HISTORY_DIR_REFINED will be created if it does not exist,
   assuming DO_REFINEDIAG is also set

See README.md for general configuration instructions.
################################################################################
'''
    print(validate_error)
    
def print_run_instructions():
    '''
    run_instructions from prior wrapperscript
    '''
    run_instructions = '''
    ##################################thin the source. My bad for not catching it earlier when I'm the one who added it and not trying to understand what it is more before adding it in. I'm not sure how Carolyn's changes to fre pp checkout were able to successfully be updated recently, bec##############################################
FRE Canopy frepp wrapper to start Canopy postprocessing workflow with
traditional Bronx frepp usage.

Cylc implementation current settings used by this wrapper:
1. Workflow name is <expname>__<platform>__<target>
e.g. use cylc commands such as:

cylc workflow-state <expname>__<platform>__<target>

This is somewhat overly verbose and also not verbose enough
(i.e. does not include FRE STEM).
If you have suggestions please let the FRE team know.

2. Will not use unique run directories.
If the run directory exists you will need to remove it before re-installing.
thin the source. My bad for not catching it earlier when I'm the one who added it and not trying to understand what it is more before adding it in. I'm not sure how Carolyn's changes to fre pp checkout were able to successfully be updated recently, bec
################################################################################
What does this script do?
1. If workflow run-dir was previously installed,thin the source. My bad for not catching it earlier when I'm the one who added it and not trying to understand what it is more before adding it in. I'm not sure how Carolyn's changes to fre pp checkout were able to successfully be updated recently, bec
   start postprocessing for a history file segment:

- Check if the workflow is running
- Check the task states
- Start cylc scheduler
- Trigger requested processing (-t YYYY)
- Exit

2. Otherwise, if workflow src-dir does not exist,
   configure the postprocessing:

- Checkout a fresh PP template
- Run the XML converter

3. Then, install and start the postprocessing for a history file segment
- Run the validation scripts
- Install the workflow
- Start cylc scheduler
- Trigger requested processing (-t YYYY)
thin the source. My bad for not catching it earlier when I'm the one who added it and not trying to understand what it is more before adding it in. I'm not sure how Carolyn's changes to fre pp checkout were able to successfully be updated recently, bec
################################################################################
Recovery steps and scenarios:
1. Something is terribly wrong withthin the source. My bad for not catching it earlier when I'm the one who added it and not trying to understand what it is more before adding it in. I'm not sure how Carolyn's changes to fre pp checkout were able to successfully be updated recently, bec PP and you want to reconfigure and try again
- Stop cylc scheduler with "cylc stop --kill <name>"
- Remove run directory with "cylc clean <name>"
- Edit the configuration files in ~/cylc-src/<name>
- Run frepp again to reinstall and run the updated PP configuration.

2. Something is terribly wrong and you want a complete fresh start,
   or you want an update from the pp template repo.
- Stop cylc scheduler with "cylc stop <name> --kill"
- Remove run directory with "cylc clean <name>"
- Remove src directory with "rm -rf ~/cylc-src/<name>"
- Run frepp again to recheckout pp template, run xml converter, and install/run

################################################################################
Specific suggestions to recover from task failures:

1. refineDiag script failures are likely with a XML-converted configs
   for two reasons, so you will probably need to either adjust or remove them.
   To disable refineDiag,
   - set DO_REFINEDIAG=False, and
   - comment out HISTORY_DIR_REFINED

a. It may use something in the XML, using an xml shell variable that does not
   exist now. In these cases, you could rewrite the refineDiag script to
   not use the xmlDir shell variable or not use the script.
   For "refineDiag_atmos_cmip6.csh", it was included in the postprocessing
   template checkout with a small modification. Use this location:
   '\$CYLC_WORKFLOW_RUN_DIR/etc/refineDiag/refineDiag_atmos_cmip6.csh'.
   - set REFINEDIAG_SCRIPTS to that location

b. It may be a refineDiag script that does not generate .nc files
   as it was expected to do. FRE Bronx allows these side-effect refineDiags,
   and instead a new mechanism was invented for these scripts that
   do not generate netcdf output:
   - set DO_PREANALYSIS=True, and
   - PREANALYSIS_SCRIPT="/paath/to/script".

2. Many PP components in Bronx XMLs are doomed (in terms of failing to
   produce output and job failing) caused by using history files that do not
   exist, but do not cause problems for the other components. Currently,
   the Canopy pp template is not robust in terms of this error mode,
   so it's best to not process history files that do not exist.

   In the future, diag manager metadata output will provide a catalog
   of history output that the validators will check against. For now,
   a simple checker exists, but you must manually generate the
   history output list ("history-manifest" file). 

   Generate the file with a simple listing of the history tarfile.
   You can append a history_refined tarfile as well. Then, the validator
   will report on PP components you have specified
   (PP_COMPONENTS) but that do not exist in the history-manifest file.

   tar -tf /path/to/history/YYYYMMDD.nc.tar | sort > history-manifest

   To run the configuration validation:

cd ~/cylc-src/<name>
rose macro --validate

   It is a good idea to not include pp components (PP_COMPONENTS) that
   include history files that do not exist.

   In all cases it is recommended to remove validation errors.
   See README.md for general configuration instructions.
   '''
    print(run_instructions)
    

#############################################

if __name__ == '__main__':
    #runFre2Experiment()
    #First experiment - based off of runthrough at: 
    #https://docs.google.com/document/d/1FhPI4o2cbMnvW9UGyZZbkwOs5Vc3INgGHZgv4YDpCY0/edit?usp=sharing
    config_file = "/home/Carolyn.Whitlock/Code/fre-features/frepp_all/am5xml/am5.xml"
    #Please note - configuring xml to run under your account takes 3 steps: 
    #1. Copy am5xml folder under am5 role account to your account - $ARCHIVE
    # and #USER are env variables set by who owns the file (i.e. you)
    #2. Create your own PP_DIR and ANALYSIS_DIR (i.e.)
    # /nbhome/Carolyn.Whitlock/am5/am5f4b5r0/c96L65_am5f4b5r0_pdclim1850F
    # /archive/Carolyn.Whitlock/am5/am5f4b5r0/c96L65_am5f4b5r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp
    #3. Symlink to the history dir using the same path as the am5 experiment
    # ln -s /archive/oar.gfdl.am5/am5/am5f4b5r0/c96L65_am5f4b5r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/history /archive/Carolyn.Whitlock/am5/am5f4b5r0/c96L65_am5f4b5r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/history
    experiment = "c96L65_am5f4b5r0_pdclim1850F"
    platform = "gfdl.ncrc5-deploy" #all gfdl-compliant platforms start with gfdl
    target = "prod-openmp"
    runFre2pp(config_file, experiment, platform, target, branch="main", time=0000)
