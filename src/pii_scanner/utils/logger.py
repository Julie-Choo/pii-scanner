# src/pii_scanner/utils/logger.py
"""
Logging configuration
"""

import logging
import sys
from typing import Optional
from .config import get_config

def setup_logging(log_level: Optional[str] = None):
    """Setup logging configuration"""
    config = get_config()
    
    level = log_level or config.get("logging", "level", "INFO")
    format_str = config.get("logging", "format")
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from external libraries
    logging.getLogger("presidio_analyzer").setLevel(logging.WARNING)
    logging.getLogger("presidio_anonymizer").setLevel(logging.WARNING)
    logging.getLogger("spacy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

# Initialize logging on import
setup_logging()