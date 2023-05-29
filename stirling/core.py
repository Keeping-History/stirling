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
    """

    ...
