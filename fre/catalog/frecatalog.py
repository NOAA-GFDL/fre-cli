import click
from scripts import gen_intake_gfdl
from scripts import test_catalog

@click.group(help=click.style(" - access fre catalog subcommands", fg=(64,94,213)))
def catalogCli():
    pass

#@catalogCli.command()
#@click.option('-i',
#              '--input_path',
#              required=True, 
#              nargs=1)
#@click.option('-o',
#              '--output_path',
#              required=True,
#              nargs=1)
#@click.option('--filter_realm',
#              nargs=1)
#@click.option('--filter_freq',
#              nargs=1)
#@click.option('--filter_chunk', 
#              nargs=1)
#@click.option('--overwrite',
#              is_flag=True,
#              default=False)
#@click.option('--append', 
#              is_flag=True,
#              default=False)
#@click.pass_context
#def build(context, input_path, output_path, filter_realm, filter_freq, filter_chunk, overwrite,append):
#    """ - Execute fre catalog build """
#    context.forward(build_script)

@catalogCli.command()
#TODO arguments dont have help message. So consider changing arguments to options?
@click.argument('input_path',required=False,nargs=1)
#,help='The directory path with the datasets to be cataloged. E.g a GFDL PP path till /pp')
@click.argument('output_path',required=False,nargs=1)
#,help='Specify output filename suffix only. e.g. catalog')
@click.option('--config',required=False,type=click.Path(exists=True),nargs=1,help='Path to your yaml config, Use the config_template in intakebuilder repo')
@click.option('--filter_realm', nargs=1)
@click.option('--filter_freq', nargs=1)
@click.option('--filter_chunk', nargs=1)
@click.option('--overwrite', is_flag=True, default=False)
@click.option('--append', is_flag=True, default=False)
@click.pass_context
def builder(context, input_path=None, output_path=None, config=None, filter_realm=None, filter_freq=None, filter_chunk=None, overwrite=False, append=False):
    """ - Generate .csv and .json files for catalog """
    context.forward(gen_intake_gfdl.main)

@catalogCli.command()
@click.argument('json_path', nargs = 1 , required = True)
@click.argument('json_template_path', nargs = 1 , required = False)
@click.option('-tf', '--test-failure', is_flag=True, default = False, help="Errors are only printed. Program will not exit.")
@click.pass_context
def validate(context, json_path, json_template_path, test_failure):
    """ - Validate a catalog against catalog schema """
    context.forward(test_catalog.main)

if __name__ == "__main__":
    catalogCli()
