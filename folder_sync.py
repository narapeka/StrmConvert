"""Full folder synchronization logic."""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from strm_converter import StrmConverter


class FolderSync:
    """Handles full synchronization of source and target folders."""
    
    def __init__(self, source_folder: str, target_folder: str, 
                 search_string: str, replacement_string: str):
        self.source_folder = Path(source_folder)
        self.target_folder = Path(target_folder)
        self.search_string = search_string
        self.replacement_string = replacement_string
        self.converter = StrmConverter()
    
    def sync_all(self) -> Dict[str, int]:
        """
        Perform full synchronization of source to target folder.
        All files are synced, but only .strm files are converted.
        
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'errors': 0
        }
        
        if not self.source_folder.exists():
            # If source folder doesn't exist, delete entire target folder structure
            if self.target_folder.exists():
                try:
                    # Count all files before deletion
                    deleted_count = sum(1 for _ in self.target_folder.rglob("*") if _.is_file())
                    shutil.rmtree(self.target_folder)
                    stats['deleted'] = deleted_count
                except Exception as e:
                    print(f"Error deleting target folder: {e}")
                    stats['errors'] += 1
            return stats
        
        # Get all files in source folder (recursive, excluding directories)
        source_files = [f for f in self.source_folder.rglob("*") if f.is_file()]
        source_relative_paths = {
            str(f.relative_to(self.source_folder)): f 
            for f in source_files
        }
        
        # Get all files in target folder (recursive, excluding directories)
        target_files = []
        if self.target_folder.exists():
            target_files = [f for f in self.target_folder.rglob("*") if f.is_file()]
        target_relative_paths = {
            str(f.relative_to(self.target_folder)): f 
            for f in target_files
        }
        
        # Process source files (create/update)
        for rel_path, source_file in source_relative_paths.items():
            target_file = self.target_folder / rel_path
            try:
                # Check if it's a .strm file - convert it
                if source_file.suffix.lower() == '.strm':
                    # Convert and write .strm file
                    content = self.converter.convert_file(
                        source_file, 
                        self.search_string, 
                        self.replacement_string
                    )
                    self.converter.write_converted_file(target_file, content)
                else:
                    # Copy other files as-is
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                
                if target_file.exists():
                    stats['updated'] += 1
                else:
                    stats['created'] += 1
            except Exception as e:
                print(f"Error processing {source_file}: {e}")
                stats['errors'] += 1
        
        # Delete files that no longer exist in source
        for rel_path, target_file in target_relative_paths.items():
            if rel_path not in source_relative_paths:
                try:
                    target_file.unlink()
                    stats['deleted'] += 1
                except Exception as e:
                    print(f"Error deleting {target_file}: {e}")
                    stats['errors'] += 1
        
        # Remove folders that no longer exist in source (this handles empty dirs too)
        self._remove_orphaned_folders(stats)
        
        return stats
    
    def _remove_empty_dirs(self, dir_path: Path) -> None:
        """Recursively remove empty directories."""
        try:
            if dir_path.exists() and dir_path != self.target_folder:
                # Check if directory is empty
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    # Try to remove parent directory
                    self._remove_empty_dirs(dir_path.parent)
        except Exception:
            pass  # Ignore errors when removing directories
    
    def _remove_orphaned_folders(self, stats: Dict[str, int]) -> None:
        """Remove folders from target that don't exist in source."""
        if not self.target_folder.exists():
            return
        
        # Get ALL directories in source (including empty ones)
        source_dirs = set()
        if self.source_folder.exists():
            # Walk through all directories in source
            for item in self.source_folder.rglob("*"):
                if item.is_dir():
                    rel_path = str(item.relative_to(self.source_folder))
                    source_dirs.add(rel_path)
            # Also add the root (empty string represents the source folder itself)
            source_dirs.add("")
        
        # Get all directories in target
        target_dirs = set()
        if self.target_folder.exists():
            for item in self.target_folder.rglob("*"):
                if item.is_dir():
                    target_dirs.add(str(item.relative_to(self.target_folder)))
            # Also add the root
            target_dirs.add("")
        
        # Find directories in target that don't exist in source
        orphaned_dirs = target_dirs - source_dirs
        
        # Remove orphaned directories (process deepest first)
        sorted_orphaned = sorted(orphaned_dirs, key=lambda x: x.count('/') + x.count('\\'), reverse=True)
        
        for rel_dir in sorted_orphaned:
            # Skip root directory
            if rel_dir == "":
                continue
                
            target_dir = self.target_folder / rel_dir
            if target_dir.exists():
                try:
                    # Count all files in the orphaned directory before deletion
                    all_files = [f for f in target_dir.rglob("*") if f.is_file()]
                    deleted_count = len(all_files)
                    
                    # Remove the directory (only if it's orphaned, meaning it doesn't exist in source)
                    # Use rmtree to handle any remaining files/subdirs
                    shutil.rmtree(target_dir, ignore_errors=True)
                    stats['deleted'] += deleted_count
                except Exception as e:
                    print(f"Error removing orphaned directory {target_dir}: {e}")
                    stats['errors'] += 1
    
    def sync_file(self, source_file: Path) -> bool:
        """
        Sync a single file from source to target.
        .strm files are converted, other files are copied as-is.
        
        Args:
            source_file: Path to source file (can be absolute or relative to source_folder)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to absolute path if relative
            if not source_file.is_absolute():
                source_file = self.source_folder / source_file
            
            # Check if file is within source folder
            if not str(source_file).startswith(str(self.source_folder)):
                return False
            
            # Skip directories
            if source_file.is_dir():
                return False
            
            # Calculate relative path
            rel_path = source_file.relative_to(self.source_folder)
            target_file = self.target_folder / rel_path
            
            # Check if it's a .strm file - convert it
            if source_file.suffix.lower() == '.strm':
                # Convert and write .strm file
                content = self.converter.convert_file(
                    source_file,
                    self.search_string,
                    self.replacement_string
                )
                self.converter.write_converted_file(target_file, content)
            else:
                # Copy other files as-is
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
            
            return True
        except Exception as e:
            print(f"Error syncing file {source_file}: {e}")
            return False
    
    def delete_file(self, target_file: Path) -> bool:
        """
        Delete a file from target folder.
        
        Args:
            target_file: Path to target file (can be absolute or relative to target_folder)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to absolute path if relative
            if not target_file.is_absolute():
                target_file = self.target_folder / target_file
            
            # Check if file is within target folder
            if not str(target_file).startswith(str(self.target_folder)):
                return False
            
            if target_file.exists():
                # Check if it's a directory - use rmtree instead
                if target_file.is_dir():
                    shutil.rmtree(target_file, ignore_errors=True)
                else:
                    target_file.unlink()
                    # Note: We don't remove empty directories here anymore
                    # Empty directories are handled by _remove_orphaned_folders()
                    # which checks if they exist in source before removing
            
            return True
        except Exception as e:
            print(f"Error deleting file {target_file}: {e}")
            return False
    
    def move_file(self, old_path: Path, new_path: Path) -> bool:
        """
        Move/rename a file in target folder.
        
        Args:
            old_path: Old path relative to target folder
            new_path: New path relative to target folder
            
        Returns:
            True if successful, False otherwise
        """
        try:
            old_abs = self.target_folder / old_path
            new_abs = self.target_folder / new_path
            
            if old_abs.exists():
                # Create parent directory for new path
                new_abs.parent.mkdir(parents=True, exist_ok=True)
                
                # Move file
                shutil.move(str(old_abs), str(new_abs))
                
                # Remove empty directories
                self._remove_empty_dirs(old_abs.parent)
                
                return True
            return False
        except Exception as e:
            print(f"Error moving file from {old_path} to {new_path}: {e}")
            return False

