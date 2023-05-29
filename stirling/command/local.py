import subprocess
from typing import Tuple


def run(cmd) -> Tuple[int, str]:
    # Eventually, this will be a bridge to the ECU.
    cmd_output = subprocess.getstatusoutput(cmd)
    if cmd_output[0] != 0:
        raise ValueError(f"Error running command: {cmd_output[1]}")

    return cmd_output
