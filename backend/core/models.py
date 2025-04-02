from django.db import models

class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    created_at and updated_at fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class ConfigurationSetting(models.Model):
    """
    A model for storing global application configuration settings.
    """
    key = models.CharField(max_length=100, unique=True, help_text="Configuration key")
    value = models.TextField(help_text="Configuration value")
    value_type = models.CharField(
        max_length=20, 
        default="str",
        choices=[
            ("str", "String"),
            ("int", "Integer"),
            ("float", "Float"),
            ("bool", "Boolean"),
            ("json", "JSON"),
        ],
        help_text="Data type of the value"
    )
    description = models.TextField(blank=True, help_text="Description of what this setting controls")
    is_active = models.BooleanField(default=True, help_text="Whether this setting is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['key']
        verbose_name = 'Configuration Setting'
        verbose_name_plural = 'Configuration Settings'
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    def get_typed_value(self):
        """Convert the string value to its actual type."""
        if self.value_type == "str":
            return self.value
        elif self.value_type == "int":
            return int(self.value)
        elif self.value_type == "float":
            return float(self.value)
        elif self.value_type == "bool":
            return self.value.lower() in ('true', 'yes', '1')
        elif self.value_type == "json":
            import json
            try:
                return json.loads(self.value)
            except Exception:
                return {}
        return self.value