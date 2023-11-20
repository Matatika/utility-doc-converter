"""CLI entrypoint 'doc-converter' command"""

from genericpath import isdir
import click
import os

from doc_converter.utils import check_file_type, convert_to_dataset, convert_files_in_dir


@click.command()
@click.argument(
    "file_path",
    type=click.STRING,
    default=os.getenv("DOC_CONVERTER_FILE_PATH"),
)
def convert(file_path):
    """CLI entrypoint and base command"""

    if os.path.isdir(file_path):
        convert_files_in_dir(file_path)
    elif check_file_type(file_path):
        convert_to_dataset(file_path)

