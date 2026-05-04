from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['title', 'parent', 'slug', 'color', 'created_by', 'created_at', 'deleted_at']
    list_filter   = ['parent', 'deleted_at']
    search_fields = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by']

    def get_queryset(self, request):
        return Category.all_objects.all()
