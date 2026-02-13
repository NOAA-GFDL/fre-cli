''' fre cmor '''

import click

from . import cmor_find_subtool
from . import cmor_run_subtool
from . import cmor_yaml_subtool
from . import cmor_config_subtool
from .cmor_finder import make_simple_varlist

OPT_VAR_NAME_HELP="optional, specify a variable name to specifically process only filenames " + \
                  "matching that variable name. I.e., this string help target local_vars, not " + \
                  "target_vars."
VARLIST_HELP="path pointing to a json file containing directory of key/value pairs. " + \
             "the keys are the \'local\' names used in the filename, and the values " + \
             "pointed to by those keys are strings representing the name of the variable " + \
             "contained in targeted files. the key and value are often the same, " + \
             "but it is not required."
RUN_ONE_HELP="process only one file, then exit. mostly for debugging and isolating issues."
DRY_RUN_HELP="don't call the cmor_mixer subtool, just printout what would be called and move on until natural exit"
START_YEAR_HELP = 'string representing the minimum calendar year CMOR should start processing for. ' + \
                  'currently, only YYYY format is supported.'
STOP_YEAR_HELP = 'string representing the maximum calendar year CMOR should stop processing for. ' + \
                  'currently, only YYYY format is supported.'

@click.group(help=click.style(" - cmor subcommands", fg=(232,91,204)))
def cmor_cli():
    ''' entry point to fre cmor click commands '''


@cmor_cli.command()
@click.option("-y", "--yamlfile", type = str,
              help = 'YAML file to be used for parsing',
              required = True )
@click.option("-e", "--experiment", type = str,
              help = "Experiment name",
              required = True )
@click.option("-p", "--platform", type = str,
              help = "Platform name",
              required = True )
@click.option("-t", "--target", type = str,
              help = "Target name",
              required = True )
@click.option("-o", "--output", type = str, default = None,
              help = "Output file if desired", required = False)
@click.option('--run_one', is_flag = True, default = False,
              help=RUN_ONE_HELP,
              required = False)
@click.option('--dry_run', is_flag = True, default = False,
              help=DRY_RUN_HELP,
              required = False)
@click.option('--start', type=str, default=None,
              help = START_YEAR_HELP,
              required = False)
@click.option('--stop', type=str, default=None,
              help = STOP_YEAR_HELP,
              required = False)
@click.option('--print_cli_call/--no-print_cli_call', default=True,
              help = 'In dry-run mode, print the equivalent CLI invocation (default) '
                     'or the Python cmor_run_subtool() call.',
              required = False)
def yaml(yamlfile, experiment, target, platform, output, run_one, dry_run, start, stop, print_cli_call):
    """
    Processes a CMOR (Climate Model Output Rewriter) YAML configuration file. This function takes a YAML file
    and various parameters related to a climate model experiment, and processes the YAML file using the CMOR
    YAML subtool.
    """

    cmor_yaml_subtool(
        yamlfile = yamlfile,
        exp_name = experiment,
        target = target,
        platform = platform,
        output = output,
        run_one_mode = run_one,
        dry_run_mode = dry_run,
        start = start,
        stop = stop,
        print_cli_call = print_cli_call
    )

@cmor_cli.command()
@click.option("-l", "--varlist", type = str,
              help=VARLIST_HELP,
              required=False)
@click.option("-r", "--table_config_dir", type = str,
              help="directory holding MIP tables to search for variables in var list",
              required=True)
@click.option('-v', "--opt_var_name", type = str,
              help=OPT_VAR_NAME_HELP,
              required=False)
def find(varlist, table_config_dir, opt_var_name): #uncovered
    '''
    loop over json table files in config_dir and show which tables contain variables in var list/
    the tool will also print what that table entry is expecting of that variable as well. if given
    an opt_var_name in addition to varlist, only that variable name will be printed out.
    accepts 3 arguments, two of the three required.
    '''
    cmor_find_subtool(
        json_var_list = varlist,
        json_table_config_dir = table_config_dir,
        opt_var_name = opt_var_name
    )



@cmor_cli.command()
@click.option("-d", "--indir", type = str,
              help="directory containing netCDF files. keys specified in json_var_list are local " + \
                   "variable names used for targeting specific files in this directory",
              required=True)
@click.option("-l", "--varlist", type = str,
              help=VARLIST_HELP,
              required=True)
@click.option("-r", "--table_config", type = str,
              help="json file containing CMIP-compliant per-variable/metadata for specific " + \
                   "MIP table. The MIP table can generally be identified by the specific " + \
                   "filename (e.g. \'Omon\')",
              required=True)
@click.option("-p", "--exp_config", type = str,
              help="json file containing metadata dictionary for CMORization. this metadata is " + \
                   "effectively appended to the final output file's header",
              required=True)
@click.option("-o", "--outdir", type = str,
              help="directory root that will contain the full output and output directory " + \
                   "structure generated by the cmor module upon request.",
              required=True)
@click.option('--run_one', is_flag = True, default = False,
              help=RUN_ONE_HELP,
              required = False)
@click.option('-v', "--opt_var_name", type = str, default = None,
              help=OPT_VAR_NAME_HELP,
              required=False)
@click.option('-g', '--grid_label', type = str, default = None,
              help = 'label representing grid type of input data, e.g. "gn" for native or "gr" for regridded, ' + \
                     'replaces the "grid_label" field in the CMOR experiment configuration file. The label must ' + \
                     'be one of the entries in the MIP controlled-vocab file.',
              required = False)
@click.option('--grid_desc', type = str, default = None,
              help = 'description of grid indicated by grid label, replaces the "grid" field in the CMOR ' + \
                     'experiment configuration file.',
              required = False)
@click.option('--nom_res', type = str, default = None,
              help = 'nominal resolution indicated by grid and/or grid label, replaces the "nominal_resolution", ' + \
                     'replaces the "grid" field in the CMOR experiment configuration file. The entered string ' + \
                     'must be one of the entries in the MIP controlled-vocab file.',
              required = False)
@click.option('--start', type=str, default=None,
              help = START_YEAR_HELP,
              required = False)
@click.option('--stop', type=str, default=None,
              help = STOP_YEAR_HELP,
              required = False)
@click.option('--calendar', type=str, default=None,
              help = 'calendar type, e.g. 360_day, noleap, gregorian... etc',
              required = False)
def run(indir, varlist, table_config, exp_config, outdir, run_one, opt_var_name,
        grid_label, grid_desc, nom_res, start, stop, calendar):
    # pylint: disable=unused-argument
    """
    Rewrite climate model output files with CMIP-compliant metadata for down-stream publishing
    """
    cmor_run_subtool(
        indir = indir,
        json_var_list = varlist,
        json_table_config = table_config,
        json_exp_config = exp_config,
        outdir = outdir,
        run_one_mode = run_one,
        opt_var_name = opt_var_name,
        grid = grid_desc,
        grid_label = grid_label,
        nom_res = nom_res,
        start = start,
        stop = stop,
        calendar_type = calendar
    )

@cmor_cli.command()
@click.option("-d", "--dir_targ", type=str, required=True, help="Target directory")
@click.option("-o", "--output_variable_list", type=str, required=True, help="Output variable list file")
@click.option("-t", "--mip_table", type=str, required=False, default=None, help="Target MIP table for making variable list")
def varlist(dir_targ, output_variable_list, mip_table):
    """
    Create a simple variable list from netCDF files in the target directory.
    """
    make_simple_varlist(dir_targ = dir_targ,
                        output_variable_list = output_variable_list,
                        json_mip_table = mip_table)


@cmor_cli.command()
@click.option("-p", "--pp_dir", type=str, required=True,
              help="Root post-processing directory containing per-component subdirectories.")
@click.option("-t", "--mip_tables_dir", type=str, required=True,
              help="Directory containing MIP table JSON files.")
@click.option("-m", "--mip_era", type=str, required=True,
              help="MIP era identifier, e.g. 'cmip6' or 'cmip7'.")
@click.option("-e", "--exp_config", type=str, required=True,
              help="Path to JSON experiment/input configuration file expected by CMOR.")
@click.option("-o", "--output_yaml", type=str, required=True,
              help="Path for the output CMOR YAML configuration file.")
@click.option("-d", "--output_dir", type=str, required=True,
              help="Root output directory for CMORized data.")
@click.option("-l", "--varlist_dir", type=str, required=True,
              help="Directory in which per-component variable list JSON files are written.")
@click.option("--freq", type=str, default="monthly",
              help="Temporal frequency string, e.g. 'monthly', 'daily'. Default 'monthly'.")
@click.option("--chunk", type=str, default="5yr",
              help="Time chunk string, e.g. '5yr', '10yr'. Default '5yr'.")
@click.option("--grid", type=str, default="g99",
              help="Grid label anchor name, e.g. 'g99', 'gn'. Default 'g99'.")
@click.option("--overwrite", is_flag=True, default=False,
              help="Overwrite existing variable list files.")
@click.option("--calendar", type=str, default="noleap",
              help="Calendar type, e.g. 'noleap', '360_day'. Default 'noleap'.")
def config(pp_dir, mip_tables_dir, mip_era, exp_config, output_yaml,
           output_dir, varlist_dir, freq, chunk, grid, overwrite, calendar):
    """
    Generate a CMOR YAML configuration file from a post-processing directory tree.
    Scans pp_dir for components and time-series data, cross-references against MIP tables,
    and writes a YAML configuration that 'fre cmor yaml' can consume.
    """
    cmor_config_subtool(
        pp_dir=pp_dir,
        mip_tables_dir=mip_tables_dir,
        mip_era=mip_era,
        exp_config=exp_config,
        output_yaml=output_yaml,
        output_dir=output_dir,
        varlist_dir=varlist_dir,
        freq=freq,
        chunk=chunk,
        grid=grid,
        overwrite=overwrite,
        calendar_type=calendar
    )
