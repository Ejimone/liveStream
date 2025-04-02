from django.contrib import admin
from .models import ConfigurationSetting

@admin.register(ConfigurationSetting)
class ConfigurationSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_display', 'value_type', 'is_active', 'updated_at')
    list_filter = ('value_type', 'is_active', 'created_at', 'updated_at')
    search_fields = ('key', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('key', 'value', 'value_type', 'is_active')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_display(self, obj):
        """Format the value for display in list view."""
        if obj.value_type == 'json':
            return "<JSON data>"
            
        if len(obj.value) > 50:
            return f"{obj.value[:50]}..."
        return obj.value
    
    value_display.short_description = 'Value'