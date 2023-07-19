"""Core

The core Stirling module, holding all the standard class definitions,
helper functions and variables we need.
"""

from abc import ABC

from pydantic.dataclasses import dataclass

import inspect


@dataclass
class StirlingClass(ABC):
    """StirlingClass is the base class for all Stirling objects.

    This class adds helper functions that all Stirling objects will use.

    Author's Note: If I'm being completely honest, I really wanted all
    the classes to inherit from here so that I could diagram them more easily.
    """

    def __post_init__(self):
        self._catch_errors()

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
