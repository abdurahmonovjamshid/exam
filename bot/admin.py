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
import openpyxl
from django.http import HttpResponse
from django.utils.timezone import localtime


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
# ----------------------

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    # Show all fields dynamically, including new comments field
    list_display = [
        field.name
        for field in JobApplication._meta.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]

    search_fields = ("user__first_name", "user__last_name", "phone_number", "comments")
    list_filter = ("status", "position", "location", "region")

    actions = ["export_to_excel"]

    def export_to_excel(self, request, queryset):
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Job Applications"

        # Get all non-many fields
        fields = [
            field
            for field in JobApplication._meta.get_fields()
            if not field.many_to_many and not field.one_to_many
        ]

        # Header row
        headers = [field.name for field in fields]
        ws.append(headers)

        # Data rows
        for app in queryset:
            row = []
            for field in fields:
                value = getattr(app, field.name)

                # Convert related objects to string
                if hasattr(value, "all"):
                    value = ", ".join([str(i) for i in value.all()])
                elif hasattr(value, "__str__") and field.is_relation:
                    value = str(value) if value else ""

                # Convert timezone-aware datetimes to naive
                if hasattr(value, "tzinfo") and value.tzinfo is not None:
                    value = localtime(value).replace(tzinfo=None)

                row.append(value)
            ws.append(row)

        # Prepare HTTP response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=job_applications.xlsx"
        wb.save(response)
        return response

    export_to_excel.short_description = "Export selected Job Applications to Excel"
# -----------------------
# PageContent
# -----------------------
@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("id", "key")
    search_fields = ("key", "text")
