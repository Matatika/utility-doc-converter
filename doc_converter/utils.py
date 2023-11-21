import tempfile
from pathlib import Path

import click
import mammoth
import pdf2docx
import yaml
from matatika.dataset import DatasetV0_2

SUPPORTED_FILE_TYPES = [
    ".doc",
    ".docx",
    ".pdf",
]


def is_supported_file(file: Path):
    return file.suffix in SUPPORTED_FILE_TYPES


def convert_docx_to_md(docx: Path):
    with docx.open("rb") as f:
        return mammoth.convert_to_markdown(f)


def convert_to_dataset(file: Path):
    if not is_supported_file(file):
        click.secho(f"Skipping {file}...")
        return

    click.echo(f"Converting {file}...")

    if file.suffix == ".pdf":
        with tempfile.TemporaryDirectory(prefix="doc-converter-") as tmp_dir:
            tmp_docx = Path(tmp_dir) / f"{file.stem}.docx"

            pdf_converter = pdf2docx.Converter(str(file))
            pdf_converter.convert(str(tmp_docx))
            pdf_converter.close()

            result = convert_docx_to_md(tmp_docx)
    else:
        result = convert_docx_to_md(file)

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
