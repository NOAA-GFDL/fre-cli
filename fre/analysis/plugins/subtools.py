import importlib
import inspect
from pathlib import Path
import pkgutil

from ..base_class import AnalysisScript
from .esnb import freanalysis_esnb


class UnknownPluginError(BaseException):
    """Custom exception for when an invalid plugin name is used."""
    pass


def _find_plugin_class(module):
    """Looks for a class that inherits from AnalysisScript.

    Args:
        module: Module object.

    Returns:
        Class that inherits from AnalysisScript.

    Raises:
        UnknownPluginError if no class is found.
    """
    for attribute in vars(module).values():
        # Try to find a class that inherits from the AnalysisScript class.
        if inspect.isclass(attribute) and AnalysisScript in attribute.__bases__:
            # Return the class so an object can be instantiated from it later.
            return attribute
    raise UnknownPluginError("could not find class that inherts from AnalysisScripts")


_sanity_counter = 0  # How much recursion is happening.
_maximum_craziness = 100  # This is too much recursion.


def _recursive_search(name, ispkg):
    """Recursively search for a module that has a class that inherits from AnalysisScript.

    Args:
        name: String name of the module.
        ispkg: Flag telling whether or not the module is a package.

    Returns:
        Class that inherits from AnalysisScript.

    Raises:
        UnknownPluginError if no class is found.
        ValueError if there is too much recursion.
    """
    global _sanity_counter
    _sanity_counter += 1
    if _sanity_counter > _maximum_craziness:
        raise ValueError(f"recursion level {_sanity_counter} too high.")

    module = importlib.import_module(name)
    try:
        return _find_plugin_class(module)
    except UnknownPluginError:
        if not ispkg:
            # Do not recurse further.
            raise
        paths = module.__spec__.submodule_search_locations
        for finder, subname, ispkg in pkgutil.iter_modules(paths):
            subname = f"{name}.{subname}"
            try:
                return _recursive_search(subname, ispkg)
            except UnknownPluginError:
                # Didn't find it, so continue to iterate.
                pass


# Dictionary of found plugins.
_discovered_plugins = {}
for finder, name, ispkg in pkgutil.iter_modules():
    if name.startswith("freanalysis_") and ispkg:
        _sanity_counter = 0
        _discovered_plugins[name] = _recursive_search(name, True)


def _plugin_object(name):
    """Attempts to create an object from a class that inherits from AnalysisScript in
       the plugin module.

    Args:
        name: Name of the plugin.

    Returns:
        The object that inherits from AnalysisScript.

    Raises:
        UnknownPluginError if the input name is not in the disovered_plugins dictionary.
    """
    return freanalysis_esnb()
#    try:
        #return _discovered_plugins[name]()
#        return freanalysis_esnb()
#    except KeyError:
#        raise UnknownPluginError(f"could not find analysis script plugin '{name}'.")


def available_plugins():
    """Returns a list of plugin names."""
    return sorted(list(_discovered_plugins.keys()))


def list_plugins():
    """Prints a list of plugin names."""
    names = available_plugins()
    if names:
        print("\n".join(["Available plugins:", "-"*32] + names))
    else:
        print("Warning: no plugins found.")


def plugin_requirements(name):
    """Returns a JSON string detailing the plugin's requirement metadata.

    Args:
        name: Name of the plugin.

    Returns:
        JSON string of metadata.
    """
    return _plugin_object(name).requires()


def run_plugin(script_type, name, config, date_range, scripts_dir, output_dir, output_yaml, pp_dir):
    """Runs the plugin's analysis.

    Args:
        name: Name of the plugin.
        catalog: Path to the data catalog.
        png_dir: Directory where the output figures will be stored.
        config: Dictionary of configuration values.
        catalog: Path to the catalog of reference data.
        pp_dir: Directory to input pp files

    Returns:
        A list of png figure files that were created by the analysis.
    """
    return _plugin_object(script_type).run_analysis(config, name, date_range, scripts_dir, output_dir, output_yaml, pp_dir)
