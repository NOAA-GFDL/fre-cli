from pathlib import Path
from subprocess import CalledProcessError, PIPE, run, STDOUT
from tempfile import TemporaryDirectory
import venv


def _process_output(output):
    """Converts bytes string to list of String lines.

    Args:
        output: Bytes string.

    Returns:
        List of strings.
    """
    return [x for x in output.decode("utf-8").split("\n") if x]


class VirtualEnvManager(object):
    """Helper class for creating/running simple command in a virtual environment."""
    def __init__(self, path):
        self.path = Path(path)
        self.activate = f"source {self.path / 'bin' / 'activate'}"

    @staticmethod
    def _execute(commands):
        """Runs input commands through bash in a child process.

        Args:
            commands: List of string commands.

        Returns:
            List of string output.
        """
        with TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "script"
            with open(script_path, "w") as script:
                script.write("\n".join(commands))
            try:
                process = run(["bash", str(script_path)], stdout=PIPE, stderr=STDOUT,
                              check=True)
            except CalledProcessError as err:
                for line in _process_output(err.output):
                    print(line)
                raise
            return _process_output(process.stdout)

    def _execute_python_script(self, commands):
        """Runs input python code in bash in a child process.

        Args:
            commands: List of string python code lines.

        Returns:
            List of string output.
        """
        with TemporaryDirectory() as tmp:
            script_path = Path(tmp) / "python_script"
            with open(script_path, "w") as script:
                script.write("\n".join(commands))
            commands = [self.activate, f"python3 {str(script_path)}"]
            return self._execute(commands)

    def create_env(self):
        """Creates the virtual environment."""
        venv.create(self.path, with_pip=True)

    def destroy_env(self):
        """Destroys the virtual environment."""
        raise NotImplementedError("this feature is not implemented yet.")

    def install_package(self, name):
        """Installs a package in the virtual environment.

        Args:
            name: String name of the package.

        Returns:
            List of string output.
        """
        commands = [self.activate, "python3 -m pip --upgrade pip",
                    f"python3 -m pip install {name}"]
        return self._execute(commands)

    def list_plugins(self):
        """Returns a list of plugins that are available in the virtual environment.

        Returns:
            List of plugins.
        """
        python_script = [
            "from analysis_scripts import available_plugins",
            "for plugin in available_plugins():",
            "    print(plugin)"
        ]
        return self._execute_python_script(python_script)

    def run_analysis_plugin(self, name, catalog, output_directory, config=None):
        """Returns a list of paths to figures created by the plugin from the virtual
           environment.

        Args:
             name: String name of the analysis package.
             catalog: Path to the data catalog.
             output_directory: Path to the output directory.

        Returns:
            List of figure paths.
        """
        if config:
            python_script = [f"config = {str(config)}",]
        else:
            python_script = ["config = None",]
        python_script += [
            "from analysis_scripts import run_plugin",
            f"paths = run_plugin('{name}', '{catalog}', '{output_directory}', config=config)",
            "for path in paths:",
            "    print(path)"
        ]
        return self._execute_python_script(python_script)

    def uninstall_package(self, name):
        """Uninstalls a package from the virtual environment.

        Args:
            name: String name of the package.

        Returns:
            List of string output.
        """
        commands = [self.activate, f"pip uninstall {name}"]
        return self._execute(commands)
