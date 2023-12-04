import os
from pathlib import Path
from typing import Tuple


def ratio_string_to_ints(namer: str) -> Tuple[int, int]:
    b = namer.split("x", 1)
    if len(b) == 2:
        try:
            return int(b[0]), int(b[1])
        except:
            raise ValueError("One of the items was not an integer.")


def load_class_module_names(directory: Path | str):
    """Load all class names from a directory.

    This is a helper utility function for loading all class names from a
    directory. It is used in the __init__.py files.json to enable the use of
    `from stirling.codecs.audio import *` and similar, as a simple
    time saver."""

    if isinstance(directory, str):
        directory = Path(directory)

    directory = directory.parent

    return [
        item[: -len(".py")]
        for item in list(
            filter(
                lambda item: item.endswith(".py") and not item.startswith("_"),
                os.listdir(directory),
            )
        )
    ]
