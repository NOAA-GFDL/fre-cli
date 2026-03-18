#python wrapper for rename_split_to_pp
#used for generating data

import sys
import os
import subprocess
import pprint

def call_rename_split_to_pp(inputDir, outputDir, history_source, do_regrid):
    '''
    Calls rename-split-to-pp, which takes 4 environment variables:
      inputDir (inputDir)  - location of your input files, output from split-netcdf
      outputDir (outputDir) - location to which to write your output files
      component (history_source) - VERY BADLY NAMED. What split-netcdf is calling the hist_source after the rewrite.
      use_subdirs (do_regrid) - either set to 1 or unset. 1 is used for the regridding case.  
    '''
    os.environ["inputDir"]  = inputDir
    os.environ["outputDir"] = outputDir
    os.environ["component"] = history_source
    print("do_regrid " + do_regrid)
    if do_regrid == "True":
        print("do_regrid is set to True")
        os.environ["use_subdirs"] = "True"
    else:
       os.environ["use_subdirs"] = "False"
    #rename-split-to-pp is a bash script in app/rename-split-to-pp/bin
    #and this file is in app/rename-split-to-pp/tests/test-data/rename-split-to-pp-wrapper.py  
    ##and this file is currently located 3 directories up from the root of the repo
    thisloc = os.path.abspath(__file__).split("/")
    app_loc = "/".join(thisloc[:-3]) + "bin/rename-split-to-pp"
    print("calling rename-split-to-pp")
    out0 = subprocess.run(app_loc, capture_output=True)
    pprint.pp(out0.stdout.split(b"\n"), width=240)
    pprint.pp(out0.stderr.split(b"\n"), width=240)
    return out0.returncode
    
if __name__ == "__main__":
    print(len(sys.argv))
    if len(sys.argv) == 5:
        call_rename_split_to_pp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Wrong number of args: we need 4 for to call rename-split-to-pp, got " + str(len(sys.argv) - 1))
        sys.exit(2)

    
