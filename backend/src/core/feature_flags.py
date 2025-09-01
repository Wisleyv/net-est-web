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
        """Load feature flags from YAML file.

        Tries multiple candidate locations to support running from repo root
        or from the backend package (tests often run with different CWD).
        """
        try:
            # Candidate paths to check (in order)
            candidates = [Path(self.config_path)]

            # If this module lives under backend/src/core, allow backend/config
            # as a fallback location used in this repository layout.
            module_root = Path(__file__).resolve().parents[2]  # backend/
            candidates.append(module_root / self.config_path)

            # Also allow an explicit backend/config absolute path from repo root
            candidates.append(Path('backend') / self.config_path)

            loaded = False
            for cfg in candidates:
                if cfg.exists():
                    with open(cfg, 'r', encoding='utf-8') as f:
                        self.flags = yaml.safe_load(f) or {}
                    loaded = True
                    break

            if not loaded:
                # No config found; keep flags empty but avoid raising.
                self.flags = {}
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