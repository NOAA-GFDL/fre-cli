''' fre pp trigger '''

import subprocess

def trigger(experiment, platform, target, time):
    """
    Trigger the pp-starter task for the time indicated
    """

    name = experiment + '__' + platform + '__' + target
    cmd = f"cylc trigger {name}//{time}/pp-starter"
    subprocess.run(cmd, shell=True, check=True, timeout=30)


if __name__ == "__main__":
    trigger()
