from os import getenv
from pathlib import Path

from requests import get, post
from yaml import safe_load


_dora_token = getenv("DORA_TOKEN")
_production_dora_url = "https://dora.gfdl.noaa.gov"


def _get_request(url, params=None):
    """Sends a get request to the input url.

    Args:
        url: String url to send the get request to.
        params: Dictionary of data that will be passed as URL parameters.

    Returns:
        Dictionary of response body data and string response text.

    Raises:
        ValueError if the response does not return status 200.
    """
    response = get(url, params)
    if response.status_code != 200:
        print(response.text)
        return ValueError("get from {url} failed.")
    return response.json(), response.text


def _post_request(url, data, auth):
    """Post an http request to a url.

    Args:
        url: String url to post the http request to.
        data: Dictionary of data that will be sent in the body of the request.
        auth: String authentication username.

    Returns:
        String text from the http response.

    Raises:
        ValueError if the response does not return status 200.
    """
    response = post(url, json=data, auth=(auth, None))
    if response.status_code != 200:
        print(response.text)
        raise ValueError(f"post to {url} with {data['expName']} failed.")
    return response.text


def _parse_experiment_yaml_for_dora(path):
    """Parse the experiment yaml and return a dictionary of the data needed to add the
       experiment to dora.

    Args:
        path: Path to the experiment yaml.

    Returns:
        Dictionary of data needed to add the experiment to dora.

    Raises:
        ValueError if the experiment owner cannot be determined.
    """
    with open(path) as file_:
        yaml_ = safe_load(file_)

        # Determine the username - is this a hack?
        history_path_parts = Path(yaml_["directories"]["history_dir"]).parts
        user = history_path_parts[2]
        if user == "$USER":
            user = getenv(user[1:])
        if not user:
            raise ValueError(f"Could not identify user {user}.")

        # Expand the paths.
        pp_path = yaml_["directories"]["pp_dir"].replace("$USER", user)
        database_path = pp_path.replace("archive", "home").replace("pp", "db") # Nasty hack.
        analysis_path = yaml_["directories"]["analysis_dir"].replace("$USER", user)

        # Get the model type from the history directory path - is there a better way?
        model_type = history_path_parts[3].upper() # Nasty hack.

        # Get the starting and ending years and total length of the experiment.
        start = int(yaml_["postprocess"]["settings"]["pp_start"])
        stop = int(yaml_["postprocess"]["settings"]["pp_stop"])
        length = stop - start + 1

        return {
            "expLength": length,
            "expName": yaml_["name"],
            "expType": yaml_["name"].split("_")[-1].upper(), # Nasty hack.
            "expYear": start,
            "modelType": model_type,
            "owner": user,
            "pathAnalysis": analysis_path.rstrip("/"),
            "pathDB": database_path.rstrip("/"),
            "pathPP": pp_path.rstrip("/"),
            "pathXML": path.rstrip("/"),
            "userName": user,
        }


def add_experiment_to_dora(experiment_yaml, dora_url=None):
    """Adds the experiment to dora using a http request.

    Args:
        experiment_yaml: Path to the experiment yaml.
        dora_url: String URL for dora.
    """
    # Parse the experiment yaml to get the data needed to add the experiment to dora.
    data = _parse_experiment_yaml_for_dora(experiment_yaml)
    data["token"] = _dora_token

    # Add the experiment to dora.
    url = dora_url or _production_dora_url
    return _get_request(f"{url}/api/add", data)[1]


def get_dora_experiment_id(experiment_yaml, dora_url=None):
    """Gets the experiment id using a http request after parsing the experiment yaml.

    Args:
        experiment_yaml: Path to the experiment yaml.
        dora_url: String URL for dora.

    Returns:
        Integer dora experiment id.

    Raises:
        ValueError if the unique experiment (identified by the pp directory path)
        cannot be found.
    """
    # Parse the experiment yaml to get the data needed to get the experiment id from.
    data = _parse_experiment_yaml_for_dora(experiment_yaml)

    # Get the experiment id from dora.
    url = dora_url or _production_dora_url
    response = _get_request(f"{url}/api/search?search={data['owner']}")
    for experiment in response[0].values():
        if experiment["pathPP"] and experiment["pathPP"].rstrip("/") == data["pathPP"]:
            return int(experiment["id"])
    raise ValueError("could not find experiment with pp directory - {data['pathPP']}")


def publish_analysis_figures(name, experiment_yaml, figures_yaml, dora_url=None):
    """Uploads the analysis figures to dora.

    Args:
        name: String name of the analysis script.
        experiment_yaml: Path to the experiment yaml file.
        figures_yaml: Path to the yaml that contains the figure paths.
        dora_url: String URL for dora.
    """
    # Check to make sure that the experiment was added to dora and get it id.
    dora_id = get_dora_experiment_id(experiment_yaml)

    # Parse out the list of paths from the input yaml file and upload them.
    url = dora_url or _production_dora_url
    url = f"{url}/api/add-png"
    data = {"id": dora_id, "name": name}
    with open(figures_yaml) as file_:
        paths = safe_load(file_)["figure_paths"]
        for path in paths:
            data["path"] = path
            _post_request(url, data, _dora_token)
