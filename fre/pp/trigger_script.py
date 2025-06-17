"""fre pp trigger"""

import subprocess


def trigger(experiment=None, platform=None, target=None, time=None):
    """
    Trigger the pp-starter task for the time indicated
    """
    if None in [experiment, platform, target, time]:
        raise ValueError(
            "experiment, platform, target and time must all not be None."
            "currently, their values are..."
            f"{experiment} / {platform} / {target} / {time}"
        )

    name = experiment + "__" + platform + "__" + target
    cmd = f"cylc trigger {name}//{time}/pp-starter"
    subprocess.run(cmd, shell=True, check=True, timeout=30)


if __name__ == "__main__":
    trigger()
