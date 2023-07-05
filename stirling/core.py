"""Core

The core Stirling module, holding all the standard class definitions,
helper functions and variables we need.
"""

from abc import ABC

from pydantic.dataclasses import dataclass


@dataclass
class StirlingClass(ABC):
    """StirlingClass is the base class for all Stirling objects.

    This class adds helper functions that all Stirling objects will use.

    (Author's Note: If I'm being completely honest, I really wanted all
    the classes to inherit from here so I could diagram them more easily.)
    """

    ...
