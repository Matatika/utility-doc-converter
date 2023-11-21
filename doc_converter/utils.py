from pathlib import Path

import click
import mammoth
import yaml
from matatika.dataset import DatasetV0_2

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

    dataset = DatasetV0_2()
    dataset.title = file.stem
    dataset.description = markdown

    dataset_yml = file.parent / f"{file.stem}.yml"

    data = {
        **dict.fromkeys(("version",)),
        **dataset.to_dict(apply_translations=False),
    }

    with dataset_yml.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
