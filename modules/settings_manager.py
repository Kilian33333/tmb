"""Settings manager - loads, saves, and validates game settings"""
import json
import os

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "music_volume": 100,
    "sound_effects_volume": 100,
    "particle_intensity": 100,
    "screen_type": 0
}

# Global settings state
_current_settings = None

def load_settings():
    """Load settings from JSON, with error handling and defaults"""
    global _current_settings
    
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                
            # Validate all required keys exist
            for key in DEFAULT_SETTINGS:
                if key not in data:
                    raise ValueError(f"Missing settings key: {key}")
            
            # Validate value ranges
            if not (0 <= data["music_volume"] <= 120):
                raise ValueError("Invalid music_volume range")
            if not (0 <= data["sound_effects_volume"] <= 120):
                raise ValueError("Invalid sound_effects_volume range")
            if not (0 <= data["particle_intensity"] <= 100):
                raise ValueError("Invalid particle_intensity range")
            if not isinstance(data["screen_type"], int) or not (0 <= data["screen_type"] <= 2):
                raise ValueError("Invalid screen_type")
            
            _current_settings = data
            return data
        else:
            # File doesn't exist, create with defaults
            _current_settings = DEFAULT_SETTINGS.copy()
            save_settings(_current_settings)
            return _current_settings
            
    except Exception as e:
        print(f"settings critical error, error: {e}, settings set to default.")
        _current_settings = DEFAULT_SETTINGS.copy()
        save_settings(_current_settings)
        return _current_settings

def save_settings(settings):
    """Save settings to JSON file"""
    global _current_settings
    try:
        _current_settings = settings
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"settings critical error, error: {e}, settings set to default.")
        _current_settings = DEFAULT_SETTINGS.copy()
        with open(SETTINGS_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=2)

def get_settings():
    """Get current settings (loads if not loaded)"""
    global _current_settings
    if _current_settings is None:
        load_settings()
    return _current_settings.copy()

def set_setting(key, value):
    """Update a single setting and save"""
    global _current_settings
    if _current_settings is None:
        load_settings()
    
    settings = _current_settings.copy()
    settings[key] = value
    save_settings(settings)

def get_setting(key):
    """Get a single setting value"""
    if _current_settings is None:
        load_settings()
    return _current_settings.get(key, DEFAULT_SETTINGS.get(key))

def reset_to_defaults():
    """Reset all settings to defaults"""
    _current_settings = DEFAULT_SETTINGS.copy()
    save_settings(_current_settings)
