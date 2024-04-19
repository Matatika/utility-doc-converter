from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

import click
import jsonlines
import mammoth
import ocrmypdf
import pdf2docx
import yaml
from matatika.dataset import DatasetV0_2

from doc_converter.converters.taps import tap_beautifulsoup

SUPPORTED_FILE_TYPES = [
    ".doc",
    ".docx",
    ".pdf",
    ".out",
]

SUPPORTED_TAP_OUTPUTS = {
    "tap-beautifulsoup.out": tap_beautifulsoup.convert_record_to_dataset,
}


def multiline_string_representer(dumper: yaml.Dumper, data: str):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, multiline_string_representer)


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


def convert_to_dataset(file: Path, output_dir: Path | None):
    if not is_supported_file(file):
        click.secho(f"Skipping {file}...")
        return

    click.echo(f"Converting {file}...")

    if file.suffix == ".out":
        convert_tap_output_to_dataset(file, output_dir)
    else:
        convert_file_to_dataset(file, output_dir)


def convert_tap_output_to_dataset(out_file: Path, output_dir: Path | None):
    if out_file.suffix != ".out":
        raise ValueError(f"{out_file.name} not an .out file")

    if out_file.name not in SUPPORTED_TAP_OUTPUTS:
        raise ValueError(f"{out_file.name} not suppored")

    convert_record_to_dataset = SUPPORTED_TAP_OUTPUTS[out_file.name]

    with out_file.open() as f:
        for singer_message in jsonlines.Reader(f):
            if singer_message["type"] != "RECORD":
                continue

            convert_record_to_dataset(
                singer_message["record"], output_dir or out_file.parent
            )


def convert_file_to_dataset(file: Path, output_dir: Path | None):
    if file.suffix == ".pdf":
        description = convert_pdf_to_description(file)
    else:
        description = convert_docx_to_description(file)

    if not description:
        click.echo(f"Nothing to do for {file}")
        return

    description = add_tags_to_description(file, description)

    write_dataset(
        title=file.stem,
        description=description,
        dataset_yml=(output_dir or file.parent) / f"{file.stem}.yml",
    )


def write_dataset(title: str, description: str, dataset_yml: Path):
    dataset = DatasetV0_2()
    dataset.source = os.getenv("DOC_CONVERTER_SOURCE", "Documents")
    dataset.title = title
    dataset.description = description.encode("ascii", errors="ignore").decode()

    data = {
        **dict.fromkeys(("version",)),
        **dataset.to_dict(apply_translations=False),
    }

    with dataset_yml.open("w") as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            sort_keys=False,
        )
