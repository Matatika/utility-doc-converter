"""Unittest module for doc-converter utility"""

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
