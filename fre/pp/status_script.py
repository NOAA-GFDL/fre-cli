"""fre pp status"""

import subprocess

TIMEOUT_SECS = 120  # 30


def status_subtool(experiment=None, platform=None, target=None):
    """
    Report workflow state for the Cylc workflow
    <experiment>__<platform>__<target>
    """
    if None in [experiment, platform, target]:
        raise ValueError(
            "experiment, platform, and target must all not be None."
            "currently, their values are..."
            f"{experiment} / {platform} / {target}"
        )

    name = experiment + "__" + platform + "__" + target
    cmd = f"cylc workflow-state {name}"
    subprocess.run(cmd, shell=True, check=True, timeout=TIMEOUT_SECS)


if __name__ == "__main__":
    status_subtool()
