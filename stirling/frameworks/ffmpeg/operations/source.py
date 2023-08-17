from pathlib import Path


def input_command(source: Path):
    return f"-i {source.resolve()}"
