"""Strm file path conversion logic."""
from pathlib import Path
from typing import Optional


class StrmConverter:
    """Converts .strm file paths using search/replace rules."""
    
    @staticmethod
    def convert_file(source_path: Path, search_string: str, replacement_string: str) -> str:
        """
        Convert .strm file content by replacing first occurrence of search_string.
        
        Args:
            source_path: Path to source .strm file
            search_string: String to search for
            replacement_string: String to replace with
            
        Returns:
            Converted file content as string
        """
        try:
            # Read source file with UTF-8 encoding
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace first occurrence only (skip if search_string is empty for sync without conversion)
            if search_string and search_string in content:
                content = content.replace(search_string, replacement_string, 1)
            
            return content
        except Exception as e:
            raise ValueError(f"Failed to convert file {source_path}: {e}")
    
    @staticmethod
    def write_converted_file(target_path: Path, content: str) -> None:
        """
        Write converted content to target .strm file.
        
        Args:
            target_path: Path to target .strm file
            content: Content to write
        """
        try:
            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content with UTF-8 encoding
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise ValueError(f"Failed to write file {target_path}: {e}")

