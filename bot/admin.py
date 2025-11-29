from django.contrib import admin
from .models import (
    TgUser,
    Menu,
    JobCategory,
    Location,
    Position,
    JobApplication,
    PageContent
)


# -----------------------
# TgUser
# -----------------------
@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):
    list_display = ("id", "telegram_id", "first_name", "last_name", "username", "phone", "created_at")
    search_fields = ("telegram_id", "first_name", "last_name", "username", "phone")
    list_filter = ("created_at",)


# -----------------------
# Menu
# -----------------------
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "title")
    search_fields = ("key", "title")


# -----------------------
# JobCategory
# -----------------------
@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "icon")
    search_fields = ("name",)


# -----------------------
# Location
# -----------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "region", "address")
    search_fields = ("name", "region", "address")
    list_filter = ("category", "region")


# -----------------------
# Position
# -----------------------
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category")
    search_fields = ("title", "category__name")
    list_filter = ("category",)


# -----------------------
# JobApplication
# -----------------------
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "position",
        "location",
        "region",
        "district",
        "phone_number",
        "birth_date",
        "status",
        "created_at",
    )

    search_fields = ("user__first_name", "user__last_name", "phone_number")
    list_filter = ("status", "position", "location", "region")


# -----------------------
# PageContent
# -----------------------
@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("id", "key")
    search_fields = ("key", "text")
