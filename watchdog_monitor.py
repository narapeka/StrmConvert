"""File system monitoring using watchdog."""
import time
import threading
import shutil
from pathlib import Path
from typing import Dict, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from folder_sync import FolderSync


class StrmFileHandler(FileSystemEventHandler):
    """Handler for file system events. Handles all file types, with special conversion for .strm files."""
    
    def __init__(self, folder_sync: FolderSync, source_folder: Path):
        super().__init__()
        self.folder_sync = folder_sync
        self.source_folder = source_folder
        self.pending_events: Dict[str, float] = {}  # path -> timestamp
        self.debounce_time = 0.5  # seconds
    
    def _get_relative_path(self, path: Path) -> Path:
        """Get path relative to source folder."""
        try:
            return path.relative_to(self.source_folder)
        except ValueError:
            return path
    
    def _process_event(self, event_path: Path, is_dir: bool = False):
        """Process file system event with debouncing."""
        rel_path = self._get_relative_path(event_path)
        current_time = time.time()
        
        # Debounce: wait a bit before processing to handle rapid events
        self.pending_events[str(rel_path)] = current_time
        
        def process_after_delay():
            time.sleep(self.debounce_time)
            if str(rel_path) in self.pending_events:
                timestamp = self.pending_events.pop(str(rel_path))
                # Only process if this is still the latest event for this path
                if timestamp == current_time:
                    if is_dir:
                        self._handle_directory_event(event_path)
                    else:
                        self._handle_file_event(event_path)
        
        thread = threading.Thread(target=process_after_delay, daemon=True)
        thread.start()
    
    def _handle_file_event(self, event_path: Path):
        """Handle a file event for any file type."""
        # Skip directories
        if event_path.is_dir():
            return
        
        if event_path.exists():
            # File created or modified - sync it (converts .strm, copies others)
            self.folder_sync.sync_file(event_path)
        else:
            # File deleted
            rel_path = self._get_relative_path(event_path)
            self.folder_sync.delete_file(rel_path)
    
    def _handle_directory_event(self, event_path: Path):
        """Handle a directory event."""
        rel_path = self._get_relative_path(event_path)
        target_dir = self.folder_sync.target_folder / rel_path
        
        if not event_path.exists():
            # Directory deleted from source - remove corresponding directory from target
            if target_dir.exists():
                try:
                    # Use shutil.rmtree to remove the entire directory tree
                    # This handles subfolders and files recursively
                    shutil.rmtree(target_dir, ignore_errors=True)
                    # Note: We don't remove parent directories here
                    # They will be handled by sync_all if needed
                except Exception as e:
                    print(f"Error handling directory deletion {event_path}: {e}")
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation event."""
        self._process_event(Path(event.src_path), is_dir=event.is_directory)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification event."""
        if not event.is_directory:
            self._process_event(Path(event.src_path))
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file/directory deletion event."""
        event_path = Path(event.src_path)
        if event.is_directory:
            # Handle directory deletion
            self._process_event(event_path, is_dir=True)
        else:
            # Handle file deletion
            rel_path = self._get_relative_path(event_path)
            self.folder_sync.delete_file(rel_path)
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file/directory move/rename event."""
        old_path = Path(event.src_path)
        new_path = Path(event.dest_path)
        
        if event.is_directory:
            # Handle directory move/rename
            old_rel = self._get_relative_path(old_path)
            new_rel = self._get_relative_path(new_path)
            
            if new_path.exists():
                # Directory was moved/renamed - sync all files in the new location
                for file in new_path.rglob("*"):
                    if file.is_file():
                        self.folder_sync.sync_file(file)
                
                # Delete old directory structure if it exists
                old_target_dir = self.folder_sync.target_folder / old_rel
                if old_target_dir.exists():
                    # Use shutil.rmtree to remove the entire directory tree
                    try:
                        shutil.rmtree(old_target_dir, ignore_errors=True)
                        self.folder_sync._remove_empty_dirs(old_target_dir.parent)
                    except Exception:
                        pass
            else:
                # Directory was moved out - delete from target
                old_rel = self._get_relative_path(old_path)
                old_target_dir = self.folder_sync.target_folder / old_rel
                if old_target_dir.exists():
                    # Use shutil.rmtree to remove the entire directory tree
                    try:
                        shutil.rmtree(old_target_dir, ignore_errors=True)
                        self.folder_sync._remove_empty_dirs(old_target_dir.parent)
                    except Exception:
                        pass
        else:
            # Handle file move/rename
            old_rel = self._get_relative_path(old_path)
            new_rel = self._get_relative_path(new_path)
            
            # If source file still exists, sync it (it was moved/renamed)
            # This handles all file types, not just .strm
            if new_path.exists() and new_path.is_file():
                self.folder_sync.sync_file(new_path)
                # Delete old target file if it exists
                self.folder_sync.delete_file(old_rel)
            else:
                # File was moved out or deleted
                self.folder_sync.delete_file(old_rel)


class WatchdogMonitor:
    """Manages file system monitoring for multiple folders."""
    
    def __init__(self):
        self.observers: Dict[str, Observer] = {}
        self.folder_syncs: Dict[str, FolderSync] = {}
        self.lock = threading.Lock()
        self.running = False
    
    def start_monitoring(self, record_id: str, source_folder: str, target_folder: str,
                        search_string: str, replacement_string: str) -> bool:
        """
        Start monitoring a source folder.
        
        Args:
            record_id: Unique identifier (UUID) for this monitoring record
            source_folder: Path to source folder
            target_folder: Path to target folder
            search_string: Search string for replacement
            replacement_string: Replacement string
            
        Returns:
            True if started successfully, False otherwise
        """
        with self.lock:
            if record_id in self.observers:
                return False  # Already monitoring
            
            source_path = Path(source_folder)
            if not source_path.exists():
                return False
            
            # Create folder sync instance
            folder_sync = FolderSync(source_folder, target_folder, 
                                   search_string, replacement_string)
            self.folder_syncs[record_id] = folder_sync
            
            # Create event handler
            event_handler = StrmFileHandler(folder_sync, source_path)
            
            # Create and start observer
            observer = Observer()
            observer.schedule(event_handler, str(source_path), recursive=True)
            observer.start()
            
            self.observers[record_id] = observer
            self.running = True
            
            return True
    
    def stop_monitoring(self, record_id: str) -> bool:
        """
        Stop monitoring a specific folder.
        
        Args:
            record_id: UUID identifier of the record to stop monitoring
            
        Returns:
            True if stopped successfully, False otherwise
        """
        observer = None
        with self.lock:
            if record_id not in self.observers:
                return False
            
            observer = self.observers[record_id]
            # Remove from dict before stopping to avoid lock issues
            del self.observers[record_id]
            if record_id in self.folder_syncs:
                del self.folder_syncs[record_id]
            
            if not self.observers:
                self.running = False
        
        # Stop and join outside the lock to avoid deadlock
        if observer is not None:
            try:
                observer.stop()
                # Wait for observer to stop, but don't block forever
                if observer.is_alive():
                    observer.join(timeout=2)
                    # If still alive after timeout, continue anyway
                    if observer.is_alive():
                        print(f"Warning: Observer {record_id} did not stop within timeout")
            except Exception as e:
                print(f"Error stopping observer {record_id}: {e}")
        
        return True
    
    def stop_all(self):
        """Stop all monitoring."""
        observers_to_stop = []
        with self.lock:
            # Get all observers and clear the dict
            observers_to_stop = list(self.observers.items())
            self.observers.clear()
            self.folder_syncs.clear()
            self.running = False
        
        # Stop all observers outside the lock
        for record_id, observer in observers_to_stop:
            try:
                observer.stop()
                if observer.is_alive():
                    observer.join(timeout=1)  # Shorter timeout for bulk stop
                    if observer.is_alive():
                        print(f"Warning: Observer {record_id} did not stop within timeout")
            except Exception as e:
                print(f"Error stopping observer {record_id}: {e}")
    
    def is_monitoring(self, record_id: str) -> bool:
        """Check if a record is being monitored."""
        with self.lock:
            return record_id in self.observers
    
    def get_status(self) -> Dict[str, bool]:
        """Get monitoring status for all records."""
        with self.lock:
            return {record_id: True for record_id in self.observers.keys()}
    
    def sync_record(self, record_id: str) -> Optional[Dict[str, int]]:
        """
        Perform full sync for a specific record.
        
        Args:
            record_id: UUID identifier of the record to sync
            
        Returns:
            Sync statistics or None if record not found
        """
        with self.lock:
            if record_id not in self.folder_syncs:
                return None
            
            return self.folder_syncs[record_id].sync_all()

