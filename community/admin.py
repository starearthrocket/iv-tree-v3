from django.contrib import admin

from .models import CommunityPost


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'is_published',
        'created_at',
    )
    list_filter = (
        'is_published',
        'created_at',
    )
    search_fields = (
        'title',
        'content',
        'author__username',
    )