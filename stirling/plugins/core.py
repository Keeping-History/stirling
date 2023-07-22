import pathlib
from abc import ABC, abstractmethod
from typing import List

from pydantic.dataclasses import dataclass

from stirling.core import StirlingClass


@dataclass
class StirlingPluginAssets(StirlingClass):
    """The assets output from a plugin that can be used by other plugins.

    This is not the same as the commands expected output. Assets are files specifically
    declared for use outside the plugin; the expected outputs are only for
    the command runner to verify that the plugin ran successfully.

    Attributes:
        name (str): The name of unique name given to the asset. This will be
            used by other plugins to reference this asset.
        path (str): The full path to the asset.
    """

    name: str
    path: pathlib.Path | None


from pydantic import BaseModel


@dataclass
class StirlingPluginOptions(StirlingClass):
    ...


@dataclass(kw_only=True)
class StirlingPlugin(StirlingClass, ABC):
    """StirlingPlugin is the base class for all plugins.

    Any plugin class definition should use this as its parent class.

    Attributes:
        name (str): The name of unique name given to the asset. This will be
            used by other plugins to reference this asset.
        assets (list, optional): A list of StirlingPluginAssets that the plugin exports
            for use by other plugins.
    """

    name: str
    depends_on: List["StirlingPlugin"] | None = None
    assets: List[StirlingPluginAssets] | None = None
    priority: int = 0

    @abstractmethod
    def cmds(self, job):
        """Returns a list of commands to be run by the plugin.

        Commands should be sorted so that, if one command requires the output of another,
        it should (obviously) be run after.

        Returns:
            list: A list of commands to be run by the plugin.
        """

        ...

    @abstractmethod
    def outputs(self, job):
        """Returns a list of the expected outputs of the plugin."""
        ...
