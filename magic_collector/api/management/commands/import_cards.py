import re
from datetime import datetime, timezone

from tqdm import tqdm

from magic_collector.api.constants import (
    CARD_IMAGE_URL,
    EXTERNAL_IDENTIFIERS,
    Color,
    FrameEffect,
    Language,
    Type,
)
from magic_collector.api.management.commands._base_import import BaseImportCommand
from magic_collector.api.models import (
    Artist,
    Card,
    Import,
    Set,
)
from magic_collector.api.schemas.card_import_schema import IMPORT_SCHEMA

LANGUAGES = {
    "arabic": Language.AR,
    "chinese simplified": Language.ZH_CN,
    "chinese traditional": Language.ZH_TW,
    "english": Language.EN,
    "french": Language.FR,
    "german": Language.DE,
    "hebrew": Language.HE,
    "italian": Language.IT,
    "japanese": Language.JP,
    "korean": Language.KO,
    "portuguese (brazil)": Language.PR_BR,
    "russian": Language.RU,
    "sanskrit": Language.SA,
    "spanish": Language.ES,
}


class Command(BaseImportCommand):
    help = "Import cards from MTGJSON All Printings database."
    import_type = Import.Type.CARDS
    schema = IMPORT_SCHEMA
    file_name = "AllPrintings"

    def import_data(self, data: dict, options: dict) -> int:
        sets_to_skip = []
        if self.options["first_run"]:
            self._stdout_message("Overwriting existing data (first run)")
            Set.objects.all().delete()
        else:
            sets_to_skip.extend(
                [card_set.code for card_set in Set.objects.filter(is_partial=False)]
            )

        # Import sets and cards
        existing_artists = {artist.name: artist for artist in Artist.objects.all()}

        bulk_cards = []

        if self.options["quiet"]:
            sets = data["data"].items()
        else:
            sets = tqdm(
                data["data"].items(),
                desc=f"{self.stdout_prefix()} Importing cards",
                bar_format="{desc} |{bar}| {percentage:3.0f}%",
            )

        for code, edition in sets:
            # Skip online only sets
            if code.lower() in sets_to_skip or edition.get("isOnlineOnly"):
                continue

            # Keep paper cards only and skip "funny" cards
            cards_by_uid = {
                card["uuid"]: card
                for card in edition["cards"]
                if not card.get("isFunny") and "paper" in card["availability"]
            }

            # Get card set data
            if cards_by_uid:
                card_set, __ = Set.objects.update_or_create(
                    code=code.lower(),
                    defaults={
                        "name": edition["name"],
                        "release_date": datetime.strptime(
                            edition["releaseDate"], "%Y-%m-%d"
                        ).replace(tzinfo=timezone.utc),
                        "translations": {
                            LANGUAGES.get(key.lower(), Language.OTHER): value
                            for key, value in edition["translations"].items()
                        },
                        "is_partial": edition.get("isPartialPreview", False),
                    },
                )
            else:
                continue

            already_added = []

            i = 0
            for uid, card_data in cards_by_uid.items():
                if uid in already_added:
                    continue

                # Get card artist data
                artist_data = card_data.get("artist")
                if artist_data:
                    try:
                        artist = existing_artists[artist_data]
                    except KeyError:
                        artist = Artist.objects.create(name=artist_data)
                        existing_artists[artist_data] = artist
                else:
                    artist = None

                # Get sides
                sides = []
                for face_uid in {uid, *card_data.get("otherFaceIds", [])}:
                    if face_uid in already_added:
                        continue

                    try:
                        data = cards_by_uid[face_uid]
                    except KeyError:
                        continue

                    if (
                        card_data["number"] in data["number"]
                        or data["number"] in card_data["number"]
                    ):
                        sides.append(data)

                # Sorting sides to get front then back
                sorted_sides = sorted(sides, key=lambda n: n["number"])

                front_versions = self.build_versions_data(sorted_sides[0], "front")
                available_languages = list(front_versions.keys())
                if len(sorted_sides) > 1:
                    back_meta = self.build_side_data(sorted_sides[1])
                    back_versions = self.build_versions_data(sorted_sides[1], "back")
                    available_languages.extend(list(back_versions.keys()))
                else:
                    back_meta = {}
                    back_versions = {}

                i += 1

                bulk_cards.append(
                    Card(
                        uid=uid,
                        set=card_set,
                        number=card_data["number"],
                        index=i,
                        external_identifiers=self.get_external_identifiers(card_data),
                        artist=artist,
                        rarity=card_data["rarity"],
                        border_color=card_data["borderColor"],
                        available_finishes=",".join(card_data["finishes"]),
                        available_frame_effects=",".join(
                            [
                                effect
                                for effect in card_data.get("frameEffects", [])
                                if effect in FrameEffect.values
                            ]
                        ),
                        available_languages=",".join(list(set(available_languages))),
                        front_meta=self.build_side_data(sorted_sides[0]),
                        back_meta=back_meta,
                        front_versions=front_versions,
                        back_versions=back_versions,
                    )
                )
                already_added.extend([side["uuid"] for side in sorted_sides])

        self._stdout_message("Saving cards...")
        cards = Card.objects.bulk_create(
            bulk_cards,
            batch_size=10_000,
            update_conflicts=True,
            unique_fields=["uid"],
            update_fields=[
                "index",
                "number",
                "set",
                "artist",
                "rarity",
                "border_color",
                "available_finishes",
                "available_frame_effects",
                "available_languages",
                "front_meta",
                "back_meta",
                "front_versions",
                "back_versions",
            ],
        )
        self._stdout_message("Cards saved")

        return len(cards)

    @staticmethod
    def get_image_url(uid: str, image_side: str = "front") -> str | None:
        """
        Get card image from Scryfall database.
        Warning: URLs have not been checked and may return a 404.
        """
        if not uid:
            return ""
        format_data = {"dir1": uid[0], "dir2": uid[1], "scryfall_id": uid}
        return CARD_IMAGE_URL.format(side=image_side, **format_data)

    @staticmethod
    def get_int_from_string(s: str) -> int:
        """
        Match power and toughness values from string and convert to int.
        """
        match = re.fullmatch(r"-?[0-9]+", s)
        return int(match.group(0)) if match else 0

    @staticmethod
    def clean_text_mana(text: str | None) -> str | None:
        """
        Remove slashes from formatted mana in card text.
        """
        if not text:
            return ""

        clean_text = ""
        split_text = text.split("}")
        for substring in split_text:
            for char in substring:
                if char == "{":
                    start = substring.index("{") + 1
                    end = len(substring)
                    mana_data = substring[start:end].replace("/", "")
                    clean_text += "{" + mana_data + "}"
                    break
                clean_text += char
        return clean_text

    def get_external_identifiers(self, data) -> dict[str, str]:
        identifiers = data["identifiers"]
        return {
            local_id: identifiers.get(mtgjson_id)
            for local_id, mtgjson_id in EXTERNAL_IDENTIFIERS.items()
        }

    def build_side_data(self, side):
        colors = side["colors"]
        if not colors:
            color_type = Color.COLORLESS
        elif len(colors) > 1:
            color_type = Color.MULTI
        else:
            color_type = colors[0]

        types = ["", ""]
        for t, card_type in enumerate(
            [t.lower() for t in side["types"] if t.lower() in Type.values]
        ):
            types[t] = card_type

        return {
            "color_definition": color_type,
            "colors": colors,
            "type1": types[0],
            "type2": types[1],
            "mana": side.get("manaCost", "").replace("/", ""),
            "mana_value": side["manaValue"],
            "power": side.get("power", ""),
            "power_value": self.get_int_from_string(side.get("power", "")),
            "toughness": side.get("toughness", ""),
            "toughness_value": self.get_int_from_string(side.get("toughness", "")),
        }

    def build_versions_data(self, side, image_side):
        versions = {}
        for version in [side, *side.get("foreignData", [])]:
            versions[LANGUAGES.get(version["language"].lower(), Language.OTHER)] = {
                "name": version["name"],
                "text": self.clean_text_mana(version.get("text", "")),
                "flavor_text": version.get("flavorText", ""),
                "type": version.get("type", ""),
                "image_url": self.get_image_url(
                    version["identifiers"].get("scryfallId", ""), image_side
                ),
            }
        return versions
