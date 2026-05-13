import click
from fre.yamltools.converters.converters import CompileConverter, PlatformConverter

@click.command("convert", short_help="tool to convert compile and platform xmls to yamls")
@click.option(
    "--xmlfile", "-x",
    type=str,
    required=True,
    help="input XML filename"
)
@click.option(
    "--experiment-name", "-e",
    type=str,
    default=None,
    help="""
    experiment name corresponding to the "name" attribute in the xml element <experiment name="experiment-name">
    If provided, only the xml body under experiment-name will be converted.
    If not provided, all experiments in xmlfile will be converted.
    """
)
@click.option(
    "--convert-compile-xml", "-c",
    is_flag=True,
    default=False,
    help="""
    Flag to only convert compile xml to yaml. 
    If not provided, convert will attempt to convert both compile and platform xmls to platforms.
    """
)
@click.option(
    "--convert-platform-xml", "-p",
    is_flag=True,
    default=False,
    help="""
    Flag to only convert platform xml to yaml.
    If not provided, convert will attempt to convert both compile and platform xmls to platforms.
    """
)
@click.pass_context
def convert(ctx, xmlfile, experiment_name, convert_compile_xml, convert_platform_xml):

    """
    Click command to convert compile and platform XML files to YAML files.
    """

    convert_both = not convert_compile_xml and not convert_platform_xml

    if convert_compile_xml or convert_both:
        compilexml = CompileConverter(xmlfile=xmlfile, experiment_name=experiment_name)
        compilexml.convert()    
    
    if convert_platform_xml or convert_both:
        platformxml = PlatformConverter(xmlfile=xmlfile)
        platformxml.convert()

    
if __name__ == "__main__":
    convert()
