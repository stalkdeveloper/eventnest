from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['id', 'mediable_type', 'mediable_id', 'source_type', 'file_type', 'storage_type', 'original_file_name', 'created_at']
    list_filter = ['file_type', 'storage_type', 'source_type', 'mediable_type']
    search_fields = ['original_file_name', 'mediable_type', 'source_type']
    ordering = ['-created_at']
