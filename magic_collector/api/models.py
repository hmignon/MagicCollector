import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from magic_collector.api.constants import (
    BorderColor,
    Condition,
    Finish,
    FrameEffect,
    Language,
    Rarity,
)


class User(AbstractUser):
    description = models.TextField(_("description"), blank=True, max_length=10_000)
    arena_id = models.CharField(_("arena ID"), blank=True, max_length=255)


class Import(models.Model):
    class Type(models.TextChoices):
        CARDS = "cards", _("CARDS")
        # PRICES = "prices", _("Prices")

    type = models.CharField(
        _("type"), choices=Type.choices, default=Type.CARDS, max_length=6
    )
    date = models.DateField(_("date"))
    version = models.CharField(_("version"), max_length=50, blank=True, default="")
    success = models.BooleanField(_("success"))
    fail_details = models.TextField(_("fails details"), blank=True, default="")
    total_items = models.PositiveIntegerField(_("total items"), default=0)

    class Meta:
        verbose_name = _("Import")
        verbose_name_plural = _("Imports")
        unique_together = ("date", "type")

    def __str__(self):
        return self.version


class Set(models.Model):
    code = models.CharField(_("code"), max_length=10, unique=True, primary_key=True)
    name = models.CharField(_("name"), max_length=255)
    release_date = models.DateField(_("release date"), blank=True, default="")
    is_partial = models.BooleanField(_("is partial"), default=False)
    # Format: {<Language>: <translation>}
    translations = models.JSONField(_("translations"), default=dict)

    class Meta:
        verbose_name = _("Set")
        verbose_name_plural = _("Sets")

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(_("name"), max_length=255)

    class Meta:
        verbose_name = _("Artist")
        verbose_name_plural = _("Artists")
        ordering = ("name",)

    def __str__(self):
        return self.name


class Card(models.Model):
    uid = models.UUIDField(_("UID"), unique=True, primary_key=True)
    set = models.ForeignKey(Set, verbose_name=_("set"), on_delete=models.CASCADE)
    artist = models.ForeignKey(
        Artist, verbose_name=_("artist"), on_delete=models.SET_NULL, null=True
    )
    number = models.CharField(_("number"), max_length=10)
    index = models.PositiveSmallIntegerField(_("index"))
    external_identifiers = models.JSONField(
        _("external identifiers"),
        default=dict,
        blank=True,
        null=True,
    )
    rarity = models.CharField(
        _("rarity"), max_length=11, choices=Rarity.choices, blank=True, default=""
    )
    border_color = models.CharField(
        _("border color"), choices=BorderColor.choices, max_length=10
    )
    # Multiple choice fields
    available_finishes = models.CharField(_("available finishes"))
    available_frame_effects = models.CharField(_("available frame effects"))
    available_languages = models.CharField(_("available languages"))

    front_meta = models.JSONField(_("front meta"), default=dict)
    back_meta = models.JSONField(
        _("back meta"),
        default=dict,
        blank=True,
        null=True,
    )
    front_versions = models.JSONField(
        _("front versions"),
        default=dict,
    )
    back_versions = models.JSONField(
        _("back versions"),
        default=dict,
        blank=True,
        null=True,
    )

    # Pricing info (TODO)
    # Format: {<finish>: <value>}
    # latest_prices = models.JSONField(
    #     _("latest prices"), default=dict, blank=True, null=True
    # )

    class Meta:
        verbose_name = _("Card")
        verbose_name_plural = _("Cards")

    def __str__(self):
        return f"Card_{self.uid}"


# ------ Collection -----------------------------------------------------------------


class Collection(models.Model):
    uid = models.UUIDField(_("UID"), default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    name = models.CharField(_("name"), max_length=50, unique=True)
    description = models.TextField(
        _("description"), max_length=10_000, blank=True, default=""
    )

    class Meta:
        verbose_name = _("Collection")
        verbose_name_plural = _("Collections")

    def __str__(self):
        return self.name


class Entry(models.Model):
    uid = models.UUIDField(_("UID"), default=uuid.uuid4, unique=True)
    collection = models.ForeignKey(
        Collection, verbose_name=_("collection"), on_delete=models.CASCADE
    )
    card = models.ForeignKey(Card, verbose_name=_("card"), on_delete=models.CASCADE)
    language = models.CharField(
        _("language"), choices=Language.choices, max_length=5, blank=True, default=""
    )
    finish = models.CharField(
        _("finish"), choices=Finish.choices, max_length=7, blank=True, default=""
    )
    border_color = models.CharField(
        _("border color"),
        choices=BorderColor.choices,
        max_length=10,
        blank=True,
        default="",
    )
    frame_effect = models.CharField(
        _("frame effect"),
        choices=FrameEffect.choices,
        max_length=50,
        blank=True,
        default="",
    )
    condition = models.CharField(
        _("condition"), choices=Condition.choices, max_length=2, blank=True, default=""
    )
    date_added = models.DateTimeField(_("date added"), auto_now_add=True)
    comment = models.TextField(_("comment"), max_length=10_000, blank=True, default="")

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")

    def __str__(self):
        return self.uid
