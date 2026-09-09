from django.contrib import admin

from .models import ProgressUpdate, TreeReport


@admin.register(TreeReport)
class TreeReportAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'owner',
        'status',
        'visibility',
        'location_name',
        'created_at',
    )
    list_filter = (
        'status',
        'visibility',
        'created_at',
    )
    search_fields = (
        'title',
        'description',
        'location_name',
        'what3words',
    )


@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = (
        'tree_report',
        'author',
        'status',
        'created_at',
    )
    list_filter = (
        'status',
        'created_at',
    )
    search_fields = (
        'tree_report__title',
        'description',
    )