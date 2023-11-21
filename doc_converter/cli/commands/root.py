"""CLI entrypoint 'doc-converter' command"""
import os
from pathlib import Path

import click

from doc_converter.utils import convert_to_dataset


@click.command()
@click.argument(
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    default=os.getenv("DOC_CONVERTER_FILE_PATH"),
)
def convert(file_path: Path):
    """CLI entrypoint and base command"""
    if file_path.is_dir():
        for file in file_path.iterdir():
            convert_to_dataset(file)
    else:
        convert_to_dataset(file_path)
