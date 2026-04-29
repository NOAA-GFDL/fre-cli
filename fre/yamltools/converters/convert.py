import click
from fre.yamltools.converters.converters import CompileConverter

@click.command("convert", short_help="tool to convert xml to yaml")
@click.option("--xmlfile", "-x",
              type=str,
              required=True,
              help="input XML filename"
)
@click.option("--experiment-name", "-e",
              type=str,
              default=None,
              help="""
              search tag to search for in the experiment name.
              something longer coming
              """
)
@click.option("--convert-compile-xml", "-c",
              is_flag=True,
              default=False,
              help="Flag to convert compile xml to yaml.  Either the -c or -p option must be provided.")
@click.option("--convert-platform-xml", "-p",
              is_flag=True,
              default=False,
              help="Flag to convert platform xml to yaml. Either the -c or -p option must be provided.")
@click.pass_context
def convert(ctx, xmlfile, experiment_name, convert_compile_xml, convert_platform_xml):
    
    if convert_compile_xml:
        compilexml = CompileConverter(xmlfile=xmlfile)
        compilexml.convert(experiment_name)
    elif convert_platform_xml:
        pass
    else:
        click.echo("Convert type not specified.  Please see below:")
        click.echo(ctx.get_help())

    
if __name__ == "__main__":
    convert()
