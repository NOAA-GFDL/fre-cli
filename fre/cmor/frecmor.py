''' fre cmor '''

import click

from . import cmor_find_subtool
from . import cmor_run_subtool
from . import cmor_yaml_subtool
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
def yaml(yamlfile, experiment, target, platform, output):
    """
    Processes a CMOR (Climate Model Output Rewriter) YAML configuration file.

    This function takes a YAML file and various parameters related to a climate model experiment,
    and processes the YAML file using the CMOR YAML subtool.

    Parameters:
    yamlfile (str): Path to the YAML configuration file.
    experiment (str): Name of the experiment.
    target (str): Target specification for the CMOR process.
    platform (str): Platform on which the CMOR process is being run.
    output (str): Output directory or file for the processed data.

    Raises:
    ValueError: If the yamlfile is not provided.
    """


    # if opt_var_name specified, forget the list.
    if yamlfile is None:
        raise ValueError('I need a yamlfile!!!')

    cmor_yaml_subtool(
        yamlfile = yamlfile,
        exp_name = experiment,
        target = target,
        platform = platform,
        output = output
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
def find(varlist, table_config_dir, opt_var_name):
    '''
    loop over json table files in config_dir and show which tables contain variables in var list/
    the tool will also print what that table entry is expecting of that variable as well. if given
    an opt_var_name in addition to varlist, only that variable name will be printed out.
    accepts 3 arguments, two of the three required.
    '''

    # if opt_var_name specified, forget the list.
    if opt_var_name is not None:
        varlist=None

    # custom arg requirement of "one of the two or both" in click should be implemented with
    # logic before calling context.invoke( <thingy>, *args )
    if opt_var_name is None and varlist is None:
        raise ValueError('opt_var_name and varlist cannot both be None')

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
@click.option('-v', "--opt_var_name", type = str,
              help=OPT_VAR_NAME_HELP,
              required=False)
def run(indir, varlist, table_config, exp_config, outdir, run_one, opt_var_name):
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
        opt_var_name = opt_var_name,
        run_one_mode = run_one
    )

@cmor_cli.command()
@click.option("-d", "--dir_targ", type=str, required=True, help="Target directory")
@click.option("-o", "--output_variable_list", type=str, required=True, help="Output variable list file")
def varlist(dir_targ, output_variable_list):
    """
    Create a simple variable list from netCDF files in the target directory.
    """
    make_simple_varlist(dir_targ, output_variable_list)


if __name__ == "__main__":
    cmor_cli()
