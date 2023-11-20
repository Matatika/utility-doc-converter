"""Unittest module for doc-converter utility"""

import unittest

from click.testing import CliRunner

from doc_converter.cli.commands.root import convert
from doc_converter.utils import check_file_type


class TestDocConverter(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.docx_file_path = "path/to/file.docx"
        self.markdown_file_path = "path/to/file.md"
        self.incorrect_file_ext_file_path = "path/to/file.xls"

    def tearDown(self):
        pass

    def test_convert_no_file_path(self):
        result = self.runner.invoke(convert, catch_exceptions=False)
        self.assertIn("Error", result.output)
        self.assertIs(result.exit_code, 2)

    def test_check_file_type_docx(self):
        result = check_file_type(self.docx_file_path)
        self.assertEqual(result, True)

    def test_check_file_type_markdown(self):
        result = check_file_type(self.markdown_file_path)
        self.assertEqual(result, False)

    def test_check_incorrect_file_type(self):
        result = check_file_type(self.incorrect_file_ext_file_path)
        self.assertEqual(result, False)
