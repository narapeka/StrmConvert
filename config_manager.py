"""Configuration management for StrmConvert application."""
import yaml
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class ConfigManager:
    """Manages loading and saving of YAML configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Optional[Dict[str, Any]] = None
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            # Create default config if it doesn't exist
            default_config = {
                "records": []
            }
            self.save(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            
            # Ensure records key exists
            if 'records' not in self.config:
                self.config['records'] = []
            
            # Normalize path separators only (preserve user's paths) and ensure UUIDs exist
            for record in self.config['records']:
                if 'source_folder' in record:
                    record['source_folder'] = self._normalize_path_separator(record['source_folder'])
                if 'target_folder' in record:
                    record['target_folder'] = self._normalize_path_separator(record['target_folder'])
                # Ensure each record has a UUID
                if 'id' not in record:
                    record['id'] = str(uuid.uuid4())
            
            return self.config
        except Exception as e:
            raise ValueError(f"Failed to load configuration: {e}")
    
    def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to YAML file."""
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("No configuration to save")
        
        # Ensure records key exists
        if 'records' not in config:
            config['records'] = []
        
        # Normalize path separators only (preserve user's paths) and ensure UUIDs exist
        for record in config['records']:
            if 'source_folder' in record:
                record['source_folder'] = self._normalize_path_separator(record['source_folder'])
            if 'target_folder' in record:
                record['target_folder'] = self._normalize_path_separator(record['target_folder'])
            # Ensure each record has a UUID
            if 'id' not in record:
                record['id'] = str(uuid.uuid4())
        
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            self.config = config
        except Exception as e:
            raise ValueError(f"Failed to save configuration: {e}")
    
    def validate(self, config: Optional[Dict[str, Any]] = None) -> Tuple[bool, Optional[str]]:
        """Validate configuration structure."""
        if config is None:
            config = self.config
        
        if config is None:
            return False, "Configuration is None"
        
        if 'records' not in config:
            return False, "Missing 'records' key in configuration"
        
        if not isinstance(config['records'], list):
            return False, "'records' must be a list"
        
        for i, record in enumerate(config['records']):
            # Ensure UUID exists
            if 'id' not in record:
                record['id'] = str(uuid.uuid4())
            elif not isinstance(record['id'], str):
                return False, f"Record {i} field 'id' must be a string (UUID)"
            
            required_fields = ['source_folder', 'target_folder', 'search_string', 'replacement_string']
            for field in required_fields:
                if field not in record:
                    return False, f"Record {i} missing required field: {field}"
                if not isinstance(record[field], str):
                    return False, f"Record {i} field '{field}' must be a string"
                # Allow empty strings for search_string and replacement_string (for sync without conversion)
                if field in ['source_folder', 'target_folder'] and not record[field].strip():
                    return False, f"Record {i} field '{field}' cannot be empty"
        
        return True, None
    
    def get_records(self) -> List[Dict[str, Any]]:
        """Get all configuration records."""
        if self.config is None:
            self.load()
        return self.config.get('records', [])
    
    def get_record_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a record by its UUID."""
        records = self.get_records()
        for record in records:
            if record.get('id') == record_id:
                return record
        return None
    
    def get_record_index(self, record_id: str) -> Optional[int]:
        """Get the index of a record by its UUID."""
        records = self.get_records()
        for idx, record in enumerate(records):
            if record.get('id') == record_id:
                return idx
        return None
    
    def _normalize_path_separator(self, path: str) -> str:
        """
        Normalize path separators based on the operating system.
        Preserves the path as-is, only converting separators if needed.
        
        On Windows: converts forward slashes to backslashes (but preserves UNC paths and absolute Unix-style paths)
        On Linux/Unix: converts backslashes to forward slashes
        """
        if not path:
            return path
        
        # Check if it's a Windows absolute path (starts with drive letter like C:)
        # or UNC path (starts with \\)
        is_windows_abs = len(path) >= 2 and path[1] == ':' and path[0].isalpha()
        is_unc = path.startswith('\\\\') or path.startswith('//')
        
        # On Windows, convert / to \ except for absolute Unix-style paths
        if os.name == 'nt':  # Windows
            # If it starts with / and is not a UNC path, it's a Unix-style absolute path
            # Keep it as-is (for network paths, Docker paths, etc.)
            if path.startswith('/') and not is_unc:
                return path  # Preserve Unix-style absolute paths
            # For other paths, normalize separators
            return path.replace('/', '\\')
        else:
            # On Linux/Unix, convert \ to /
            return path.replace('\\', '/')

