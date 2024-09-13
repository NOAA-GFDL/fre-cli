import fre
from fre import cmor
from fre.cmor import _cmor_run_subtool

# where are we? we're running pytest from the base directory of this repo
rootdir = 'fre/tests/test_files'

# explicit inputs to tool
indir = f'{rootdir}/ocean_sos_var_file'
varlist = f'{rootdir}/varlist'
table_config = f'{rootdir}/cmip6-cmor-tables/Tables/CMIP6_Omon.json'
exp_config = f'{rootdir}/CMOR_input_example.json'
outdir = f'{rootdir}/outdir'

# determined by cmor_run_subtool
# TODO get rid of that wildcard? how? 
full_outputdir=f"{outdir}/CMIP6/CMIP6/ISMIP6/PCMDI/PCMDI-test-1-0/piControl-withism/r3i1p1f1/Omon/sos/gn/*"
full_outputfile=f"{full_outputdir}/sos_Omon_PCMDI-test-1-0_piControl-withism_r3i1p1f1_gn_199307-199807.nc"

# FYI
filename = 'ocean_monthly_1x1deg.199301-199712.sos.nc' # unneeded, this is mostly for reference
full_inputfile=f"{indir}/{filename}"

def test_fre_cmor_run(capfd):
    ''' fre cmor run, test-use case '''

    fre.cmor._cmor_run_subtool(
        indir = indir,
        varlist = varlist,
        table_config = table_config,
        exp_config = exp_config,
        outdir = outdir
    )

    # the routine above doesn't really return anything
    # so if we get here, b.c. no internal
    # error to cmor_run_subtool raised, assert True ?
    # DOUBLE CHECK THIS ASSUMPTION!!!!!
    assert True
    out, err = capfd.readouterr()

    

    
#def test_fre_cmor_run_output_compare(capfd):
#    ''' I/O comparison of prev test-use case '''
#    assert subprocess.run( [
#                             "nccmp", "-f", "-m", "-g", "-d", 
#                            f"{full_inputfile}",
#                            f"{full_outputfile}"
#                           ],
#                           shell=True
#                         ).returncode == 1
#    out, err = capfd.readouterr()
#    #subprocess.run(["rm", "-rf", "/nbhome/Ciheim.Brown/outdir/CMIP6/CMIP6/"])
