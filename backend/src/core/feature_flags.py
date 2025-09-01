import os
import yaml
from pathlib import Path
from typing import Dict, Any

class FeatureFlags:
    """Feature flag service with hot reload capability"""
    
    def __init__(self, config_path: str = "config/feature_flags.yaml"):
        self.config_path = config_path
        self.flags: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load feature flags from YAML file"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    self.flags = yaml.safe_load(f) or {}
        except Exception as e:
            # Fallback to empty config on error
            self.flags = {}
            print(f"Error loading feature flags: {e}")
    
    def is_enabled(self, feature_path: str) -> bool:
        """
        Check if a feature is enabled using dot notation
        Example: is_enabled("experimental.sentence_alignment")
        """
        # Split dot-separated path
        parts = feature_path.split('.')
        current = self.flags
        
        # Traverse the configuration
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return False  # Feature path not found
        
        # Return boolean value if found
        return bool(current)

# Global instance for easy access
feature_flags = FeatureFlags()