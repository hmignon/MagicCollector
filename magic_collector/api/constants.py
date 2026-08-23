from django.db import models
from django.utils.translation import gettext_lazy as _

CARD_IMAGE_URL = (
    "https://cards.scryfall.io/large/{side}/{dir1}/{dir2}/{scryfall_id}.jpg"
)

EXTERNAL_IDENTIFIERS = {
    "arena": "mtgArenaId",
    "card_kingdom": "cardKingdomId",
    "card_sphere": "cardsphereId",
    "card_market": "mcmId",
    "scryfall": "scryfallId",
}


class Language(models.TextChoices):
    EN = "en", _("English")
    FR = "fr", _("French")
    AR = "ar", _("Arabic")
    ZH_CN = "zh-cn", _("Chinese simplified")
    ZH_TW = "zh-tw", _("Chinese traditional")
    DE = "de", _("German")
    HE = "he", _("Hebrew")
    IT = "it", _("Italian")
    JP = "jp", _("Japanese")
    KO = "ko", _("Korean")
    PR_BR = "pr-br", _("Portuguese (Brazil)")
    RU = "ru", _("Russian")
    SA = "sa", _("Sanskrit")
    ES = "es", _("Spanish")
    OTHER = "other", _("Other")


class Rarity(models.TextChoices):
    COMMON = "common", _("Common")
    UNCOMMON = "uncommon", _("Uncommon")
    RARE = "rare", _("Rare")
    MYTHIC = "mythic", _("Mythic")
    SPECIAL = "special", _("Special")
    BONUS = "bonus", _("Bonus")


class Color(models.TextChoices):
    BLACK = "B", _("Black")
    GREEN = "G", _("Green")
    RED = "R", _("Red")
    BLUE = "U", _("Blue")
    WHITE = "W", _("White")
    MULTI = "M", _("Multicolored")
    COLORLESS = "C", _("Colorless")


class Type(models.TextChoices):
    ARTIFACT = "artifact", _("Artifact")
    BATTLE = "battle", _("Battle")
    CREATURE = "creature", _("Creature")
    ENCHANTMENT = "enchantment", _("Enchantment")
    INSTANT = "instant", _("Instant")
    LAND = "land", _("Land")
    PLANESWALKER = "planeswalker", _("Planeswalker")
    SORCERY = "sorcery", _("Sorcery")
    TRIBAL = "tribal", _("Tribal")


class Finish(models.TextChoices):
    NONFOIL = "nonfoil", _("Non-foil")
    FOIL = "foil", _("Foil")
    ETCHED = "etched", _("Etched")
    SIGNED = "signed", _("Signed")


class BorderColor(models.TextChoices):
    BLACK = "black", _("Black")
    GOLD = "gold", _("Gold")
    SILVER = "silver", _("Silver")
    WHITE = "white", _("White")
    YELLOW = "yellow", _("Yellow")
    BORDERLESS = "borderless", _("Borderless")


class FrameEffect(models.TextChoices):
    BORDERLESS = "borderless", _("Borderless")
    COLORSHIFTED = "colorshifted", _("Colorshifted")
    COMPANION = "companion", _("Companion")
    EXTENDEDART = "extendedart", _("Extended art")
    FULLART = "fullart", _("Full art")
    LESSON = "lesson", _("Lesson")
    SAGA = "saga", _("Saga")
    SHOWCASE = "showcase", _("Showcase")
    SUNMOONDFC = "sunmoondfc", _("Sun Moon")


class Condition(models.TextChoices):
    MINT = "mt", _("Mint")
    NEAR_MINT = "nm", _("Near mint")
    EXCELLENT = "ex", _("Excellent")
    GOOD = "gd", _("Good")
    LIGHTLY_PLAYED = "lp", _("Lightly played")
    PLAYED = "pl", _("Played")
    POOR = "po", _("Poor")
