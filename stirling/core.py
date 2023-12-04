"""Core

The core Stirling module, holding all the standard class definitions,
helper functions and variables we need.
"""

import inspect
from abc import ABC
from dataclasses import asdict

from pydantic.dataclasses import dataclass


@dataclass
class StirlingClass(ABC):
    """StirlingClass is the base class for all Stirling objects.

    This class adds helper functions that all Stirling objects will use.

    Author's Note: If I'm being completely honest, I really wanted all
    the classes to inherit from here so that I could diagram them more easily.
    """

    def _catch_errors(self):
        def catch_function_error(f):
            """Handles all errors for a function in a centralized place."""

            def catcher(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except Exception as exc:
                    raise exc

            return catcher

        # Decorate all the functions in the class with the error catcher.
        for name, method in inspect.getmembers(self):
            if (
                not inspect.ismethod(method) and not inspect.isfunction(method)
            ) or inspect.isbuiltin(method):
                continue
            setattr(self, name, catch_function_error(method))

    def get_attribute_names(self):
        return list(asdict(self).keys())
