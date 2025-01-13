import click

from .subtools import add_experiment_to_dora, get_dora_experiment_id, \
                      publish_analysis_figures


@click.group(help=click.style(" - access fre dora subcommands", fg=(250, 154, 90)))
def dora_cli():
    """Entry point to fre dora click commands."""
    pass


@dora_cli.command()
@click.option("--experiment-yaml", type=str, required=True, help="Path to the experiment yaml.")
@click.option("--dora-url", type=str, required=False, help="Dora's URL.")
def add(experiment_yaml, dora_url):
    """Add an experiment to dora."""
    print(add_experiment_to_dora(experiment_yaml, dora_url))


@dora_cli.command()
@click.option("--experiment-yaml", type=str, required=True, help="Path to the experiment yaml.")
@click.option("--dora-url", type=str, required=False, help="Dora's URL.")
def get(experiment_yaml, dora_url):
    """Gets an experiment id from dora."""
    print(get_dora_experiment_id(experiment_yaml, dora_url))


@dora_cli.command()
@click.option("--name", type=str, required=True, help="Name of the analysis script.")
@click.option("--experiment-yaml", type=str, required=True,
              help="Path to the experiment yaml file.")
@click.option("--figures-yaml", type=str, required=True,
              help="Path to the yaml that contains the figure paths.")
@click.option("--dora-url", type=str, required=False, help="Dora's URL.")
def publish(name, experiment_yaml, figures_yaml, dora_url):
    """Uploads the analysis figures to dora."""
    publish_analysis_figures(name, experiment_yaml, figures_yaml, dora_url)


if __name__ == "__main__":
    dora_cli()
