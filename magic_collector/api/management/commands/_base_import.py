import json
import urllib.request
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import fastjsonschema
from django.core.management import BaseCommand, CommandError
from django.utils.timezone import now

from magic_collector.api.models import Import

BASE_URL = "https://mtgjson.com/api/v5/"


class BaseImportCommand(BaseCommand):
    import_type: Import.Type
    schema: dict
    file_name: str
    options: dict

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="Print debugging messages.",
        )
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="Do not display any stdout messages.",
        )
        parser.add_argument(
            "-s",
            "--source",
            type=Path,
            help="Path to file to use as source file.",
        )
        parser.add_argument(
            "-f",
            "--first-run",
            action="store_true",
            help=(
                "Import all data from scratch. "
                "If data already exists, it will be overwritten."
            ),
        )

    def stdout_prefix(self):
        timestamp = now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{self.import_type.value.upper()}][{timestamp}]"

    def _stdout_message(self, msg, prefix=None):
        if not self.options["quiet"]:
            self.stdout.write(f"{self.stdout_prefix()} {msg}")

    def handle(self, *args, **options):
        self.options = options

        data = self.get_json_data()
        total = self.import_data(data, options)

        self.register_import_object(total=total)
        return f"Import finished ({total} {self.import_type.value})"

    def process_error(self, exc: type[Exception], message: str):
        import_object = self.register_import_object(
            success=False, fail_details=str(exc)
        )
        self._stdout_message(message)
        if self.options["debug"]:
            self.stdout.write(str(exc))
        raise CommandError(
            f"\n\nAn error occurred while importing "
            f"the {self.import_type.value}. Details are "
            f"available in Import #{import_object.id}."
        )

    def get_json_data(self) -> dict:
        """
        Use source file of request the url,
        load the file archive and return a dict with
        the loaded JSON data.
        """
        if self.options["source"]:
            file_path = self.options["source"]
            if not file_path.exists():
                self.process_error(FileNotFoundError, "File does not exist!")
            try:
                with file_path.open() as f:
                    data = json.loads(f.read())
            except json.decoder.JSONDecodeError as e:
                self.process_error(e, "File does not exist")

        else:
            request = urllib.request.Request(
                f"{BASE_URL}{self.file_name}.json.zip",
                # User-Agent is necessary as we need to simulate
                # the request coming from a browser
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) "
                        "Gecko/20100101 Firefox/126.0"
                    )
                },
            )

            try:
                response = urllib.request.urlopen(request)
            except urllib.request.HTTPError as e:
                self.process_error(e, f"Error while fetching data ({e})!")

            self._stdout_message(
                f"{self.import_type.value.capitalize()} file downloaded"
            )

            z = ZipFile(BytesIO(response.read()))
            with z.open(f"{self.file_name}.json") as f:
                try:
                    data = json.loads(f.read())
                except json.decoder.JSONDecodeError as e:
                    self.process_error(e, "Invalid JSON!")

                self._stdout_message("Data extracted")

        validator = fastjsonschema.compile(self.schema)
        try:
            validator(data)
        except fastjsonschema.exceptions.JsonSchemaException as e:
            self.process_error(e, "Not properly formatted!")

        self._stdout_message("JSON validated")

        return data

    def register_import_object(
        self,
        success: bool = True,
        fail_details: str = "",
        total: int = 0,
    ):
        import_object, __ = Import.objects.update_or_create(
            date=now().date(),
            type=self.import_type,
            defaults={
                "success": success,
                "fail_details": fail_details,
                "total_items": total,
            },
        )
        return import_object

    def import_data(self, data: dict, options: dict) -> int:
        raise NotImplementedError
