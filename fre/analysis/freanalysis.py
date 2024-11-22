import click

from .subtools import add_experiment_to_dora, publish_analysis_figures, run_analysis


@click.group(help=click.style(" - access fre analysis subcommands", fg=(250, 154, 90)))
def analysis_cli():
    """Entry point to fre analysis click commands."""
    pass


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of the analysis script.")
@click.option("--experiment_yaml", type=str, required=True,
              help="Path to the experiment yaml file.")
@click.option("--figures_yaml", type=str, required=True,
              help="Path to the yaml that contains the figure paths.")
@click.pass_context
def publish(context, name, experiment_yaml, figures_yaml):
    """Uploads the analysis figures to dora."""
    context.forward(publish_analysis_figures)


@analysis_cli.command()
@click.option("--name", type=str, required=True, help="Name of the analysis script.")
@click.option("--catalog", type=str, required=True, help="Path to the data catalog.")
@click.option("--output_directory", type=str, required=True,
              help="Path to the output directory.")
@click.option("--output_yaml", type=str, required=True, help="Path to the output yaml.")
@click.option("--experiment_yaml", type=str, required=True, help="Path to the experiment yaml.")
@click.pass_context
def run(context, name, catalog, output_directory, output_yaml, experiment_yaml):
    """Runs the analysis script and writes the paths to the created figures to a yaml file."""
    context.forward(run_analysis)


@analysis_cli.command()
@click.option("--experiment_yaml", type=str, required=True, help="Path to the experiment yaml.")
@click.pass_context
def add(context, experiment_yaml):
    """Add an experiment to dora."""
    context.forward(add_experiment_to_dora)


if __name__ == "__main__":
    analysis_cli()
