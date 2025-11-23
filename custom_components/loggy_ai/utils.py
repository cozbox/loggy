"""Utility functions for the Loggy AI integration."""
import logging
import os
from typing import Optional

from .const import LOG_PATHS, DEFAULT_LOG_PATH

_LOGGER = logging.getLogger(__name__)

def is_systemd_available() -> bool:
    """Check if systemd journal is available on this system.
    
    Returns:
        True if systemd journal module is available and accessible, False otherwise.
    """
    try:
        from systemd import journal
        # Try to access the journal to verify it's actually usable
        _ = journal.Reader()
        return True
    except (ImportError, OSError, RuntimeError) as err:
        _LOGGER.debug(f"Systemd journal not available: {err}")
        return False

def find_log_file() -> Optional[str]:
    """Auto-detect Home Assistant log file location.
    
    Scans common log file locations and returns the first readable file found.
    A file is considered readable if it exists, is a regular file, and has read permissions.
    
    Returns:
        The absolute path to the first readable log file found, or None if no log file is found.
    """
    _LOGGER.debug("Auto-detecting Home Assistant log file location...")
    
    for log_path in LOG_PATHS:
        # Expand user home directory if present
        expanded_path = os.path.expanduser(log_path)
        
        try:
            if os.path.exists(expanded_path) and os.path.isfile(expanded_path):
                # Check if file is readable
                if os.access(expanded_path, os.R_OK):
                    _LOGGER.info(f"Auto-detected log file at: {expanded_path}")
                    return expanded_path
                else:
                    _LOGGER.debug(f"Log file exists but not readable: {expanded_path}")
        except Exception as err:
            _LOGGER.debug(f"Error checking log path {expanded_path}: {err}")
            continue
    
    _LOGGER.warning(
        f"No log file auto-detected. Checked paths: {', '.join(LOG_PATHS)}"
    )
    return None

def get_default_log_path() -> str:
    """Get the default log path, attempting auto-detection first.
    
    Returns:
        The auto-detected path if a readable log file is found, 
        otherwise returns DEFAULT_LOG_PATH as fallback.
    """
    detected_path = find_log_file()
    return detected_path if detected_path else DEFAULT_LOG_PATH
