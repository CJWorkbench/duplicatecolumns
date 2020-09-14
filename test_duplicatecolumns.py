from typing import NamedTuple
import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from cjwmodule.testing.i18n import cjwmodule_i18n_message
from duplicatecolumns import migrate_params, render


class RenderColumn(NamedTuple):
    format: str = ""


class Settings(NamedTuple):
    MAX_BYTES_PER_COLUMN_NAME: int = 100


class MigrateParamsTests(unittest.TestCase):
    def test_v0_empty(self):
        self.assertEqual(migrate_params({"colnames": ""}), {"colnames": []})

    def test_v0_nonempty(self):
        self.assertEqual(
            migrate_params({"colnames": "A,B,C"}), {"colnames": ["A", "B", "C"]}
        )

    def test_v1(self):
        self.assertEqual(
            migrate_params({"colnames": ["A", "B"]}), {"colnames": ["A", "B"]}
        )


class DuplicateColumnsTests(unittest.TestCase):
    def test_duplicate_column(self):
        table = pd.DataFrame({"A": [1, 2], "B": [2, 3], "C": [3, 4]})
        input_columns = {
            "A": RenderColumn("{:,}"),
            "B": RenderColumn("{:,.2f}"),
            "C": RenderColumn("{:,d}"),
        }
        result = render(
            table,
            {"colnames": ["A", "C"]},
            settings=Settings(),
            input_columns=input_columns,
        )
        expected = pd.DataFrame(
            {
                "A": [1, 2],
                "Copy of A": [1, 2],
                "B": [2, 3],
                "C": [3, 4],
                "Copy of C": [3, 4],
            }
        )
        assert_frame_equal(result["dataframe"], expected)
        self.assertEqual(
            result["column_formats"], {"Copy of A": "{:,}", "Copy of C": "{:,d}"}
        )

    def test_duplicate_with_existing(self):
        table = pd.DataFrame(
            {"A": [1, 2], "Copy of A": [2, 3], "Copy of A 1": [3, 4], "C": [4, 5]}
        )
        input_columns = {
            "A": RenderColumn("{:,}"),
            "Copy of A": RenderColumn("{:,.2f}"),
            "Copy of A 1": RenderColumn("{:,.1%}"),
            "C": RenderColumn("{:,d}"),
        }
        result = render(
            table, {"colnames": ["A"]}, settings=Settings(), input_columns=input_columns
        )
        expected = pd.DataFrame(
            {
                "A": [1, 2],
                "Copy of A 2": [1, 2],
                "Copy of A": [2, 3],
                "Copy of A 1": [3, 4],
                "C": [4, 5],
            }
        )
        assert_frame_equal(result["dataframe"], expected)
        self.assertEqual(result["column_formats"], {"Copy of A 2": "{:,}"})

    def test_create_too_long_column_names(self):
        table = pd.DataFrame({"AAAAAAAAAA": [1], "AAAAAAAAAB": [2]})
        input_columns = {"AAAAAAAAAA": RenderColumn(""), "AAAAAAAAAB": RenderColumn("")}
        result = render(
            table,
            {"colnames": ["AAAAAAAAAA", "AAAAAAAAAB"]},
            settings=Settings(MAX_BYTES_PER_COLUMN_NAME=12),
            input_columns=input_columns,
        )
        expected = pd.DataFrame(
            {
                "AAAAAAAAAA": [1],
                "Copy of AAAA": [1],
                "AAAAAAAAAB": [2],
                "Copy of AA 2": [2],
            }
        )
        assert_frame_equal(result["dataframe"], expected)
        self.assertEqual(
            result["errors"],
            [
                cjwmodule_i18n_message(
                    id="util.colnames.warnings.truncated",
                    arguments={
                        "n_columns": 2,
                        "first_colname": "Copy of AAAA",
                        "n_bytes": 12,
                    },
                ),
                cjwmodule_i18n_message(
                    id="util.colnames.warnings.numbered",
                    arguments={"n_columns": 1, "first_colname": "Copy of AA 2"},
                ),
            ],
        )
