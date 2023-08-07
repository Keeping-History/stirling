import pathlib
from abc import ABC, abstractmethod
from dataclasses import field, asdict
from typing import List

from pydantic.dataclasses import dataclass

from stirling.config import StirlingConfig
from stirling.core import StirlingClass
from stirling.logger import get_job_logger, StirlingJobLogger


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


@dataclass
class StirlingPluginOptions(StirlingClass):
    """The options for a plugin."""

    plugin_name: str

    def merge_default_options(self, options: dict):
        updated_options = self.default_options("audio")
        updated_options.update(options)
        return updated_options

    @staticmethod
    def defaults(plugin_name: str):
        config_path = f"plugins/{plugin_name}/defaults"
        return StirlingConfig().get(config_path) or {}

    def get_attribute_names(self):
        return list(self._to_dict().keys())

    def _to_dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

    @classmethod
    def _from_str(cls, options_dict: dict):
        mytype = type(cls)
        print(mytype)


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
    logger: StirlingJobLogger = field(default_factory=get_job_logger)

    @abstractmethod
    def cmds(self, job):
        """Returns a list of commands to be run by the plugin.

        Commands should be sorted so that, if one command requires the output of another,
        it should (obviously) be run after.

        Returns:
            list: A list of commands to be run by the plugin.
        """

        ...

    # @abstractmethod
    # def outputs(self, job):
    #     """Returns a list of the expected outputs of the plugin."""
    #     ...
