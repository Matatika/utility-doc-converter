from pathlib import Path

import click
import mammoth
import yaml

SUPPORTED_FILE_TYPES = [
    ".doc",
    ".docx",
]


def is_supported_file(file: Path):
    return file.suffix in SUPPORTED_FILE_TYPES


def convert_to_dataset(file: Path):
    if not is_supported_file(file):
        click.secho(f"Skipping {file}...")
        return

    click.echo(f"Converting {file}...")

    with file.open("rb") as f:
        result = mammoth.convert_to_markdown(f)

    markdown = result.value.replace("\\#", "#")

    dataset = {
        "version": "datasets/v0.2",
        "title": file.stem,
        "description": markdown,
    }

    dataset_path = file.parent / f"{file.stem}.yml"

    with dataset_path.open("w") as yml:
        yaml.dump(dataset, yml, default_flow_style=False)
