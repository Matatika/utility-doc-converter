import os
import re
import tempfile
from pathlib import Path

import click
import mammoth
import ocrmypdf
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


def convert_docx_to_description(docx: Path):
    with docx.open("rb") as f:
        value: str = mammoth.convert_to_markdown(f).value
        return value.replace("\\#", "#").strip()


def convert_pdf_to_description(pdf: Path):
    with tempfile.TemporaryDirectory(prefix="doc-converter-") as tmp_dir:
        tmp_docx = Path(tmp_dir) / f"{pdf.stem}.docx"

        pdf_converter = pdf2docx.Converter(str(pdf))
        pdf_converter.convert(str(tmp_docx))
        pdf_converter.close()

        md = convert_docx_to_description(tmp_docx)

        if md:
            return md

        tmp_txt = tmp_docx.with_suffix(".txt")
        ocrmypdf.ocr(pdf, os.devnull, sidecar=tmp_txt)

        return tmp_txt.read_text().strip()


def add_tags_to_description(file: Path, description: str):
    parts = [part for part in (*file.parts[:-1], file.stem)]
    tags = ["#" + re.sub(r"\W", "_", part.lower()) for part in parts]

    return description + "\n\n" + " ".join(tags)


def convert_to_dataset(file: Path):
    if not is_supported_file(file):
        click.secho(f"Skipping {file}...")
        return

    click.echo(f"Converting {file}...")

    if file.suffix == ".pdf":
        description = convert_pdf_to_description(file)
    else:
        description = convert_docx_to_description(file)

    if not description:
        click.echo(f"Nothing to do for {file}")
        return

    description = add_tags_to_description(file, description)

    dataset = DatasetV0_2()
    dataset.title = file.stem
    dataset.description = description

    dataset_yml = file.parent / f"{file.stem}.yml"

    data = {
        **dict.fromkeys(("version",)),
        **dataset.to_dict(apply_translations=False),
    }

    with dataset_yml.open("w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
