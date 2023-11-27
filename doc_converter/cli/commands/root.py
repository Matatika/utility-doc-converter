"""CLI entrypoint 'doc-converter' command"""
import os
from pathlib import Path

import click

from doc_converter.utils import convert_to_dataset


@click.command()
@click.argument(
    "file_path",
    type=click.Path(exists=True, path_type=Path),
    default=os.getenv("DOC_CONVERTER_FILE_PATH", Path.cwd()),
)
@click.option(
    "--output-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=os.getenv("DOC_CONVERTER_OUTPUT_DIR"),
)
def convert(file_path: Path, output_dir):
    """CLI entrypoint and base command"""
    if file_path.is_dir():
        for file in file_path.iterdir():
            convert_to_dataset(file, output_dir)
    else:
        convert_to_dataset(file_path, output_dir)
