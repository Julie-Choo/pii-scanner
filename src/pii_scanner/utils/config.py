# src/pii_scanner/utils/config.py
"""
Configuration management
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path

class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration"""
        self._config = {}
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None):
        """Load configuration from file and environment"""
        
        # Default configuration
        self._config = {
            "scanner": {
                "confidence_threshold": 0.5,
                "context_window": 50,
                "default_entities": [
                    "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", 
                    "CREDIT_CARD", "PERSON"
                ],
                "language": "en"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "cors_enabled": True,
                "cors_origins": ["*"]
            },
            "streamlit": {
                "port": 8501,
                "host": "0.0.0.0"
            }
        }
        
        # Load from file if provided
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    self._merge_config(self._config, file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_path}: {e}")
        
        # Override with environment variables
        self._load_from_environment()
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        env_mappings = {
            "PII_CONFIDENCE_THRESHOLD": ("scanner", "confidence_threshold", float),
            "PII_CONTEXT_WINDOW": ("scanner", "context_window", int),
            "PII_LANGUAGE": ("scanner", "language", str),
            "LOG_LEVEL": ("logging", "level", str),
            "API_HOST": ("api", "host", str),
            "API_PORT": ("api", "port", int),
            "STREAMLIT_PORT": ("streamlit", "port", int),
            "STREAMLIT_HOST": ("streamlit", "host", str)
        }
        
        for env_var, (section, key, type_converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = type_converter(value)
                    self._config[section][key] = converted_value
                except ValueError:
                    print(f"Warning: Invalid value for {env_var}: {value}")
    
    def get(self, section: str, key: str, default=None):
        """Get configuration value"""
        return self._config.get(section, {}).get(key, default)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config.get(section, {})
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()

# Global config instance
_config_instance = None

def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance