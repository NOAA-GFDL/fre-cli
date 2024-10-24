''' fre cmor '''

import click

from .cmor_mixer import _cmor_run_subtool

@click.group(help=click.style(" - access fre cmor subcommands", fg=(232,91,204)))
def cmor_cli():
    ''' entry point to fre cmor click commands '''

@cmor_cli.command()
@click.option("-d", "--indir",
              type=str,
              help="Input directory",
              required=True)
@click.option("-l", "--varlist",
              type=str,
              help="Variable list",
              required=True)
@click.option("-r", "--table_config",
              type=str,
              help="Table configuration",
              required=True)
@click.option("-p", "--exp_config",
              type=str,
              help="Experiment configuration",
              required=True)
@click.option("-o", "--outdir",
              type=str,
              help="Output directory",
              required=True)
@click.option('-v', "--opt_var_name",
              type = str,
              help="optional variable name filter. if the variable name in the targeted file doesnt match, the variable is skipped",
              required=False)
@click.pass_context
def run(context, indir, varlist, table_config, exp_config, outdir, opt_var_name):
    # pylint: disable=unused-argument
    """Rewrite climate model output"""
    context.invoke(
        _cmor_run_subtool,
        indir = indir,
        json_var_list = varlist,
        json_table_config = table_config,
        json_exp_config = exp_config,
        outdir = outdir,
        opt_var_name = opt_var_name
    )
    #    context.forward(
    #        _cmor_run_subtool() )

if __name__ == "__main__":
    cmor_cli()
