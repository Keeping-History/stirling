import uuid
from pathlib import Path
from dataclasses import dataclass
from typing import get_type_hints
from dateutil import parser as date_parser

# definitions holds all the standard class definitions and variables we need
# to run jobs.

# StirlingClass is the base class for all Stirling objects. This class adds helper functions that all Stirling objects will use.
class StirlingClass(object):

    # Define a custom function when attempting to set a class attribute
    def __setattr__(self, name, value):
        # Get the type hints from our Job
        proper_type = get_type_hints(self)[name]
        # If necessary, attempt to convert the value to the proper type we
        # expect.
        self.__dict__[name] = type_check(value, proper_type)

# Use this class definition as an example for creating your own StirlingArgsPlugin:
# @dataclass
# class StirlingArgsPlugin(StirlingClass):
#   """You can use this class as a template to
#        create a Argument extend this class and apply your own plugin settings. Just
#        to be sure to create a unique namespace for your plugin, and use it in your
#        variable naming. For example, the hls package generator plugin uses the "hls_"
#        prefix in its argument variable names."""
#    template_argument = Type or default value

# StirlingCmd objects are structures that hold the final command to run for
# a specific step in a job. A StirlingCmd must include the command to run
# in cli style, and the raw output from the command.
@dataclass
class StirlingCmd(StirlingClass):
    """StirlingCmd is the base class for command objects. These command
    objects will be converted into specific commands to run."""

    # The final, completed command that is run.
    command: str = None
    # The output from the command above
    output: str = None

# type_check attempts to set our variable to the proper type.
def type_check(value, proper_type):
    # If the type of our incoming value and the type we hinted in the
    # object, then let's try to translate it to the proper type.
    a = True
    try:
        a = isinstance(value, proper_type)
    except TypeError:
        # We can't determine the type, so set it as passed.
        value = value
    if not a:
        match proper_type.__name__:
            case "PurePath" | "PurePosixPath" | "PureWindowsPath" | "Path" | "PosixPath" | "WindowsPath":
                if value is None:
                    value = ""
                value = Path(value)
            case "UUID":
                try:
                    value = uuid.UUID(value)
                except ValueError:
                    # We must have a Job ID. If we can't set one, then we'll just create a random one.
                    value = uuid.uuid4()
            case "datetime":
                if type(value) is str and value != "":
                    value = date_parser.parse(value)
            case "float":
                value = float(str(value))
            case "int":
                value = int(float(str(value)))
            case "bool":
                if type(value) is int and (value == 0 or value == 1):
                    value = bool(value)
                elif type(value) is str:
                    match value.lower():
                        case "y" | "yes" | "t" | "true":
                            value = True
                        case "n" | "no" | "f" | "false":
                            value = False
                        case _:
                            # We may want to modify this default case later
                            # to set it to the default or get the value it
                            # already was and leave it as is.
                            value = False
                else:
                    value = False
            case _:
                if value is None:
                    # Allow a None (nil) value
                    pass

    return value
