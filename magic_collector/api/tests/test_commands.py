from io import StringIO
from pathlib import Path

from django.core.management import CommandError, call_command
from django.test import TestCase

from magic_collector.api.models import Import

TEST_DATA_PATH = Path(__file__).parent / "data"


class ImportCardsCommandTestCase(TestCase):
    def _test(self, args: dict, success=True):
        original_import_count = Import.objects.count()
        out = StringIO()
        args["quiet"] = True
        if success:
            call_command("import_cards", **args, stdout=out)
            self.assertIn("Import finished", out.getvalue())
            self.assertEqual(Import.objects.count(), original_import_count + 1)
            self.assertTrue(Import.objects.last().success)
        else:
            with self.assertRaises(CommandError):
                call_command("import_cards", **args, stdout=out)
            self.assertEqual(Import.objects.count(), original_import_count + 1)
            self.assertFalse(Import.objects.last().success)

    def test_import_cards(self) -> None:
        self._test({})

    def test_import_cards_from_file(self) -> None:
        self._test({"source": TEST_DATA_PATH / "valid_cards.json"})

    def test_import_cards_unknown_file(self) -> None:
        self._test({"source": TEST_DATA_PATH / "unknown.json"}, success=False)

    def test_import_cards_invalid_file_format(self) -> None:
        self._test({"source": TEST_DATA_PATH / "not_a_json.txt"}, success=False)

    def test_import_cards_non_compliant_formatting(self) -> None:
        self._test(
            {"source": TEST_DATA_PATH / "invalid_formatting.json"}, success=False
        )

    def test_import_cards_update(self):
        # Import once
        out = StringIO()
        call_command(
            "import_cards",
            source=TEST_DATA_PATH / "valid_cards.json",
            quiet=True,
            stdout=out,
        )
        self.assertIn("Import finished (5 cards)", out.getvalue())

        # Import again
        out = StringIO()
        call_command(
            "import_cards",
            source=TEST_DATA_PATH / "valid_cards.json",
            quiet=True,
            stdout=out,
        )
        self.assertIn("Import finished (0 cards)", out.getvalue())

    def test_import_cards_overwrite(self):
        # Import once
        out = StringIO()
        call_command(
            "import_cards",
            source=TEST_DATA_PATH / "valid_cards.json",
            quiet=True,
            stdout=out,
        )
        self.assertIn("Import finished (5 cards)", out.getvalue())

        # Import again
        out = StringIO()
        call_command(
            "import_cards",
            source=TEST_DATA_PATH / "valid_cards.json",
            first_run=True,
            quiet=True,
            stdout=out,
        )
        self.assertIn("Import finished (5 cards)", out.getvalue())

    def test_import_cards_partial(self):
        # Import once
        out = StringIO()
        call_command(
            "import_cards",
            source=TEST_DATA_PATH / "valid_cards_partial.json",
            quiet=True,
            stdout=out,
        )
        self.assertIn("Import finished (5 cards)", out.getvalue())

        # Import again
        out = StringIO()
        call_command(
            "import_cards",
            source=TEST_DATA_PATH / "valid_cards_partial.json",
            quiet=True,
            stdout=out,
        )
        self.assertIn("Import finished (5 cards)", out.getvalue())
