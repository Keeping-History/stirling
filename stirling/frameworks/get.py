from typing import List

from stirling.frameworks import AVAILABLE_FRAMEWORKS
from stirling.frameworks.base import StirlingMediaFramework


def available_frameworks() -> List[str]:
    return list(AVAILABLE_FRAMEWORKS.keys())


def get_framework(name: str) -> StirlingMediaFramework:
    return AVAILABLE_FRAMEWORKS.get(name)
