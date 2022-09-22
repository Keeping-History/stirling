from datetime import datetime
import uuid
import json
import dataclasses
import pathlib

class JobEncoder(json.JSONEncoder):
        def default(self, obj):
            if dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)
            elif isinstance(obj, uuid.UUID):
                # if the obj is uuid, we simply return the value of uuid
                return str(obj)
            elif isinstance(obj, datetime):
                return str(obj)
            elif isinstance(obj, pathlib.Path):
                return str(obj)
            elif dataclasses.is_dataclass(obj):
                return dataclasses.asdict(obj)

            return super().default(obj)
