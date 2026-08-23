from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from magic_collector.api.models import Artist, Card, Import, Set, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        *DjangoUserAdmin.fieldsets,
        (_("MagicCollector"), {"fields": ("description", "arena_id")}),
    )


@admin.register(Import)
class ImportAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "date",
        "success",
        "total_items",
    )
    date_hierarchy = "date"
    list_filter = ("success", "type")
    ordering = ("-date",)


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "release_date", "is_partial")
    list_filter = ("is_partial",)
    date_hierarchy = "release_date"
    ordering = ("release_date",)
    search_fields = (
        "code",
        "name",
    )


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    readonly_fields = ("uid",)
    list_display = (
        "set",
        "index",
        "number",
        "rarity",
    )
    list_filter = (
        "set",
        "rarity",
    )
    ordering = (
        "set__release_date",
        "index",
    )
    search_fields = (
        "uid",
        "set__code",
        "set__name",
    )
