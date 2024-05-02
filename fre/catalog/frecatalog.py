import click
from .gen_intake_gfdl import build_script

@click.group(help="- access fre catalog subcommands")
def catalogCli():
    pass

@catalogCli.command()
@click.option('-i',
              '--input_path',
              required=True, 
              nargs=1)
@click.option('-o',
              '--output_path',
              required=True,
              nargs=1)
@click.option('--filter_realm',
              nargs=1)
@click.option('--filter_freq',
              nargs=1)
@click.option('--filter_chunk', 
              nargs=1)
@click.option('--overwrite',
              is_flag=True,
              default=False)
@click.option('--append', 
              is_flag=True,
              default=False)
@click.pass_context
def build(context, input_path, output_path, filter_realm, filter_freq, filter_chunk, overwrite,append):
    """ - Execute fre catalog build """
    context.forward(build_script)

if __name__ == "__main__":
    catalogCli()
