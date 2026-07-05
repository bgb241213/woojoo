from django.contrib import admin

from .models import SalesRecord, SalesRecordImage


class SalesRecordImageInline(admin.TabularInline):
    model = SalesRecordImage
    extra = 3
    fields = ['image', 'order']


@admin.register(SalesRecord)
class SalesRecordAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'shipped_date', 'photo_key', 'is_active')
    list_filter = ('is_active', 'shipped_date')
    list_editable = ('is_active',)
    search_fields = ('model_name',)
    ordering = ('-shipped_date', '-id')
    inlines = [SalesRecordImageInline]
