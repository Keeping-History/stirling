import json
import os
import pathlib
from abc import ABC, abstractmethod
from dataclasses import field
from pathlib import Path
from typing import List, Any

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from stirling.config import StirlingConfig
from stirling.core import StirlingClass
from stirling.logger import get_job_logger, StirlingJobLogger


def load_plugins(
    options: "List[StirlingPluginOptions | dict | str]",
    directory: str | Path | None = None,
):
    """Load all plugins."""

    if directory is None:
        directory = os.path.dirname(Path(__file__).absolute())

    if isinstance(directory, str):
        directory = Path(directory)

    # Get the list of directories in the plugins directory.
    # We only want directories and ones that are properly named
    # (i.e. don't start with an underscore). We also want to make
    # sure there is a `core.py` file in the directory.
    plugin_directories = [
        item
        for item in list(
            filter(
                lambda item: not item.startswith("_")
                and not item.endswith(".py")
                and Path(directory / item / "core.py").exists(),
                os.listdir(directory),
            )
        )
    ]

    # Attempt to dynamically import the plugins and initialize them with their
    # default options.
    try:
        loaded_plugins = [
            __import__(
                f"stirling.plugins.{plugin}.core", fromlist=["get_plugin"]
            ).get_plugin()
            for plugin in plugin_directories
        ]

    except Exception as e:
        raise ImportError("Could not load plugins.") from e

    return loaded_plugins


@dataclass
class StirlingPluginAssets(StirlingClass):
    """The assets output from a plugin that can be used by other plugins.

    This is not the same as the commands expected output. Assets are files.json specifically
    declared for use outside the plugin; the expected outputs are only for
    the command runner to verify that the plugin ran successfully.

    Attributes:
        name (str): The name of unique name given to the asset. This will be
            used by other plugins to reference this asset.
        path (str): The fulla path to the asset.
    """

    name: str
    path: pathlib.Path | None


class StirlingPluginOptions(BaseModel, StirlingClass):
    """The options for a plugin."""

    plugin_name: str
    source: str | Path | None = None
    source_stream: int | None = None

    @classmethod
    def get_default_options(cls):
        class_default_options = {k: v.default for k, v in cls.__fields__.items()}
        updated_options = (
            StirlingConfig().get(
                f"plugins/{cls.__fields__.get('plugin_name').default}/defaults"
            )
            or {}
        )
        class_default_options |= updated_options
        return class_default_options

    @classmethod
    def merge_default_options(cls, options: dict):
        merge_default_options = cls.get_default_options()
        merge_default_options.update(options)
        return merge_default_options

    @classmethod
    def parse_options(cls, options: Any):
        try:
            match options:
                case cls():
                    pass
                case dict():
                    updated_options = cls.merge_default_options(options)
                    options = cls.parse_obj(updated_options)
                case None:
                    options = cls.parse_obj(cls.get_default_options())
                case _:
                    parsed_options = json.loads(options)
                    updated_options = cls.merge_default_options(parsed_options)
                    options = cls.parse_obj(updated_options)
        except Exception as e:
            raise ValueError("Could not parse options.") from e

        return options


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
    commands: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.logger.debug(f"Initializing plugin {self.name}")

    @abstractmethod
    def cmds(self, job):
        """Returns a list of commands to be run by the plugin.

        Commands should be sorted so that, if one command requires the output of
        another, it should (obviously) be run after.

        Returns:
            list: A list of commands to be run by the plugin.
        """
        ...

    # TODO: Do we need this still?
    # @abstractmethod
    # def outputs(self, job.json):
    #     """Returns a list of the expected outputs of the plugin."""
    #     ...
