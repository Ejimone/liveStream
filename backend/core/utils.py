import json
import logging
import os
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_configuration_value(key, default=None):
    """
    Get a configuration value from the database.
    
    Args:
        key (str): The configuration key
        default: The default value to return if the key is not found
        
    Returns:
        The typed configuration value or default if not found
    """
    try:
        from .models import ConfigurationSetting
        setting = ConfigurationSetting.objects.filter(key=key, is_active=True).first()
        if setting:
            return setting.get_typed_value()
        return default
    except Exception as e:
        logger.error(f"Error retrieving configuration value for {key}: {e}")
        return default

def get_unique_filename(base_path, filename):
    """
    Generate a unique filename if the given filename already exists.
    
    Args:
        base_path (str): The base directory path
        filename (str): The original filename
        
    Returns:
        str: A unique filename
    """
    # Split the filename into name and extension
    name, ext = os.path.splitext(filename)
    
    # Create the full path
    full_path = os.path.join(base_path, filename)
    
    # If the path doesn't exist, return the original filename
    if not os.path.exists(full_path):
        return filename
        
    # Otherwise, add a counter until we find a unique name
    counter = 1
    while os.path.exists(os.path.join(base_path, f"{name}_{counter}{ext}")):
        counter += 1
        
    return f"{name}_{counter}{ext}"

def get_download_directory():
    """
    Get the directory to use for downloaded files.
    
    Returns:
        str: The absolute path to the download directory
    """
    # Default to the MEDIA_ROOT/downloads directory
    download_dir = os.path.join(settings.MEDIA_ROOT, 'downloads')
    
    # Create the directory if it doesn't exist
    if not os.path.exists(download_dir):
        try:
            os.makedirs(download_dir)
        except Exception as e:
            logger.error(f"Error creating downloads directory: {e}")
            # Fall back to the system temporary directory
            import tempfile
            download_dir = tempfile.gettempdir()
    
    return download_dir

def format_date_for_display(date_value):
    """
    Format a date or datetime for display.
    
    Args:
        date_value: A date, datetime, or string date
        
    Returns:
        str: Formatted date string
    """
    if not date_value:
        return ""
    
    # If it's already a string, try to parse it
    if isinstance(date_value, str):
        try:
            date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return date_value
    
    # Format the date
    now = timezone.now()
    if isinstance(date_value, datetime):
        # If it's today
        if date_value.date() == now.date():
            return f"Today at {date_value.strftime('%I:%M %p')}"
        
        # If it's yesterday
        if date_value.date() == (now - timedelta(days=1)).date():
            return f"Yesterday at {date_value.strftime('%I:%M %p')}"
        
        # If it's within a week
        if date_value > now - timedelta(days=7):
            return date_value.strftime('%A at %I:%M %p')  # Day of week
        
        # Otherwise use full date
        return date_value.strftime('%B %d, %Y at %I:%M %p')
    else:
        # Just format the date
        return date_value.strftime('%B %d, %Y')

def safely_get_json_value(json_data, path, default=None):
    """
    Safely get a nested value from a JSON dictionary.
    
    Args:
        json_data (dict): The JSON data
        path (str): Dot-separated path to the value (e.g., "user.profile.name")
        default: The default value to return if the path is not found
        
    Returns:
        The value at the path or the default if not found
    """
    if not json_data or not isinstance(json_data, dict):
        return default
        
    parts = path.split('.')
    current = json_data
    
    try:
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    except Exception:
        return default