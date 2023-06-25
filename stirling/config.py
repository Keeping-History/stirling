import json
import os
from pathlib import Path

from stirling.core import StirlingClass

DEFAULT_CONFIG_DIRECTORY = Path('../stirling/config')
DEFAULT_CONFIG_FILE_FORMAT = 'json'
DEFAULT_PATH_SEPARATOR = '/'


class StirlingConfig(StirlingClass):
    def __init__(self, directory: Path | str | None = None):
        self._config_dict = {}
        self._config_file_format = DEFAULT_CONFIG_FILE_FORMAT

        directory = directory or DEFAULT_CONFIG_DIRECTORY
        if type(directory) is str:
            directory = Path(directory)

        if directory.is_dir():
            self._directory = directory or DEFAULT_CONFIG_DIRECTORY
            self._config_dict = self._path_to_nested_dict()

    # Public methods
    def reload(self):
        self._config_dict = self._path_to_nested_dict()

    def get(self, key: str | None = None):
        return self._get_object_by_path(key) if key else self._config_dict

    # Convenience methods
    def get_json(self, key: str | None = None) -> str:
        return json.dumps(self.get(key), indent=4)

    def to_json(self):
        return self.get_json()

    def to_dict(self):
        return self._config_dict

    # Private methods
    def _path_to_nested_dict(self):
        accumulated_dict = {}
        print(self._get_paths_for_config_files())
        for file_path in self._get_paths_for_config_files():
            object_path_array = self._get_object_path_as_array(file_path)
            print("called merge_config_dicts")
            accumulated_dict = {**self._merge_config_dicts(object_path_array, file_path), **accumulated_dict}
        return accumulated_dict

    def _merge_config_dicts(self, object_path_array, file_path):
        path_converted_dict = tmp_dict = {}

        for i, name in enumerate(object_path_array):
            print(file_path)
            config_object = self._load_json_file(file_path) or {}
            tmp_dict[name] = config_object
            tmp_dict = tmp_dict[name]
            if name == "frameworks" or name == "ffmpeg":
                print(i, name, config_object, object_path_array, tmp_dict)

        return path_converted_dict


    def _get_paths_for_config_files(self):
        return list(Path(self._directory).rglob(f"*.{self._config_file_format}"))

    def _get_object_path_as_array(self, file_path):
        relative_parent_directory = os.path.relpath(file_path.parent, self._directory)

        if relative_parent_directory.startswith(('/', '.')):
            object_path = [file_path.stem]
        else:
            object_path = f"{relative_parent_directory}/{file_path.stem}".split('/')

        return object_path

    def _get_object_by_path(self, object_path):
        if not object_path:
            return None

        rv = self._config_dict
        for key in object_path.split(DEFAULT_PATH_SEPARATOR):
            try:
                rv = rv[key]
            except KeyError:
                return None
        return rv

    @staticmethod
    def _load_json_file(file_path):
        try:
            loaded_json = json.load(open(file_path))
            print(loaded_json)

        except Exception as exc:
            raise IOError(
                f"Could not load config file for {file_path}.") from exc

        return loaded_json
