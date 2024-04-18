from pathlib import Path

import doc_converter.utils as utils


def convert_record_to_dataset(record: dict, output_dir: Path):
    source = Path(record["source"])
    page_url = record["page_url"]

    alias = ".".join([*source.parts[1:-1], source.stem])
    lines = [line.rstrip() for line in record["page_content"].splitlines()]

    utils.write_dataset(
        title=source.stem,
        description="\n\n".join(
            [
                f"# [{source.stem}]({page_url})",
                "---",
                *lines,
            ]
        ),
        dataset_yml=output_dir / f"{alias}.yml",
    )
