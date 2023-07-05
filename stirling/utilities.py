from typing import Tuple


def ratio_string_to_ints(namer: str) -> Tuple[int, int]:
    b = namer.split("x", 1)
    if len(b) == 2:
        try:
            return int(b[0]), int(b[1])
        except:
            raise ValueError("One of the items was not an integer.")
