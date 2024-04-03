"""Unittest module for doc-converter utility"""

import shutil
import tempfile
import unittest
from pathlib import Path

from click.testing import CliRunner

from doc_converter.cli.commands.root import convert
from doc_converter.utils import is_supported_file


class TestDocConverter(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_convert_file_docx(self):
        with tempfile.TemporaryDirectory(prefix="test-doc-converter-") as tmp_dir:
            shutil.copy("tests/sample_documents/Aircraft leasing.docx", tmp_dir)

            result = self.runner.invoke(convert, tmp_dir)

            self.assertIs(result.exit_code, 0)

            tmp_dir = Path(tmp_dir)

            self.assertIs((tmp_dir / "Aircraft leasing.yml").exists(), True)

    def test_convert_file_pdf(self):
        with tempfile.TemporaryDirectory(prefix="test-doc-converter-") as tmp_dir:
            shutil.copy("tests/sample_documents/Lorem Ipsum.pdf", tmp_dir)

            result = self.runner.invoke(convert, tmp_dir)

            self.assertIs(result.exit_code, 0)

            tmp_dir = Path(tmp_dir)

            self.assertIs((tmp_dir / "Lorem Ipsum.yml").exists(), True)

    def test_convert_file_pdf_ocr(self):
        with tempfile.TemporaryDirectory(prefix="test-doc-converter-") as tmp_dir:
            shutil.copy("tests/sample_documents/Facsimile transmission.pdf", tmp_dir)

            result = self.runner.invoke(convert, tmp_dir)

            self.assertIs(result.exit_code, 0)

            tmp_dir = Path(tmp_dir)

            self.assertIs((tmp_dir / "Facsimile transmission.yml").exists(), True)

    def test_convert_dir(self):
        with tempfile.TemporaryDirectory(prefix="test-doc-converter-") as tmp_dir:
            shutil.copytree("tests/sample_documents", tmp_dir, dirs_exist_ok=True)

            result = self.runner.invoke(convert, tmp_dir)

            self.assertIs(result.exit_code, 0)

            tmp_dir = Path(tmp_dir)

            self.assertTrue((tmp_dir / "Aircraft leasing.yml").exists())
            self.assertTrue((tmp_dir / "Facsimile transmission.yml").exists())
            self.assertTrue((tmp_dir / "Lorem Ipsum.yml").exists())

    def test_convert_sub_dir(self):
        with tempfile.TemporaryDirectory(prefix="test-doc-converter-") as tmp_dir:
            sub_dir = f"{tmp_dir}/sample_documents"
            shutil.copytree("tests/sample_documents", sub_dir)

            result = self.runner.invoke(convert, tmp_dir)

            self.assertIs(result.exit_code, 0)

            sub_dir = Path(sub_dir)

            self.assertTrue((sub_dir / "Aircraft leasing.yml").exists())
            self.assertTrue((sub_dir / "Facsimile transmission.yml").exists())
            self.assertTrue((sub_dir / "Lorem Ipsum.yml").exists())

    def test_convert_empty_dir(self):
        with tempfile.TemporaryDirectory(prefix="test-doc-converter-") as tmp_dir:
            result = self.runner.invoke(convert, tmp_dir)

        self.assertFalse(result.output)
        self.assertIs(result.exit_code, 0)

    def test_check_file_type_docx(self):
        file = Path("path/to/file.docx")
        is_supported = is_supported_file(file)

        self.assertTrue(is_supported)

    def test_check_file_type_markdown(self):
        file = Path("path/to/file.md")
        is_supported = is_supported_file(file)

        self.assertFalse(is_supported)

    def test_check_incorrect_file_type(self):
        file = Path("path/to/file.xls")
        is_supported = is_supported_file(file)

        self.assertFalse(is_supported)
