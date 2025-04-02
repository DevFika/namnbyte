# folder_data_manager.py
import re, os
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, deque
from typing import List
from .file_filter import FileFilter
from .signal import Signal, InformationSignal
from copy import deepcopy

ENABLED_FOLDER = f"[#A3BE8C]✓[/#A3BE8C]"
DISABLED_FOLDER = f"[#BF616A]✗[/#BF616A]"

class Folder:
    def __init__(self, folder_name: str, parent: "Folder", root_path: str = None):
        print("Creating folder")
        self.id = str(uuid.uuid4())
        self.current_name = folder_name
        self.new_name = folder_name
        self.parent = parent
        self.root_path = root_path if root_path else (parent.root_path if parent else None)
        self.is_enabled = True
        self.subfolders_populated = False
        self.files_populated = False
        self.is_populated = False
        self.files = []
        self.folders = []

    @property
    def folder_path(self) -> str:
        """Dynamically construct the folder path based on the hierarchy."""
        if self.parent and self.parent.folder_path:
            return str(Path(self.parent.folder_path) / self.current_name)

        # Ensure a valid root path is always returned
        return self.root_path or ""

    def add_file(self, file: 'File'):
        self.files.append(file)

    def add_folder(self, folder: 'Folder'):
        """Properly link child folders and ensure root_path inheritance."""
        folder.parent = self  # Set the parent reference

        # Ensure subfolder correctly inherits root_path from parent
        if not folder.root_path:
            folder.root_path = self.root_path

        self.folders.append(folder)


    def rename_folder(self, new_name: str):
        """Helper method to rename folder and update paths of files and subfolders"""
        old_folder_path = Path(self.folder_path)
        new_folder_path = old_folder_path.parent / new_name  # Keep the same parent directory

        try:
            old_folder_path.rename(new_folder_path)  # Rename the folder on disk
            self.current_name = new_name
            return True
            print(f"[DEBUG] Successfully renamed folder {self.current_name} → {new_name}")
        except Exception as e:
            print(f"[ERROR] Failed to rename folder {self.current_name} → {new_name}: {e}")
            return False

        # Update folder attributes
        self.current_name = new_name

    def update_subfolder_paths(self):
        """Recursively update the folder paths for all child folders."""
        for subfolder in self.folders:
            # Update each subfolder's folder path
            subfolder.root_path = self.root_path  # Update the root path reference
            subfolder.update_subfolder_paths()  # Recursively update paths of subfolders

        for file in self.files:
            file.folder = self

    

class File:
    def __init__(self, file_name: str, folder: 'Folder'):
        self.id = str(uuid.uuid4())
        self.current_name = file_name
        self.new_name = file_name
        self.folder = folder
        # folder_path = self.folder.folder_path or self.folder.root_path
        self.is_enabled = True
        self.file_ext = Path(file_name).suffix  # Extract actual file extension
        self.size = 0
        # if not folder_path:
        #     print(f"[WARNING] File {file_name} is missing a valid folder path!")

    @property
    def abs_path(self) -> str:
        """Dynamically compute the absolute path based on the folder reference."""
        return str(Path(self.folder.folder_path) / self.current_name)

    @property
    def rel_path(self) -> str:
        """Dynamically compute the relative path based on the root folder."""
        return Path(self.abs_path).relative_to(self.folder.root_path).as_posix()
    
    @property
    def folder_path(self) -> str:
        """Dynamically compute the relative path based on the root folder."""
        return self.folder.folder_path

    def rename_file(self, new_name: str):
        """Rename the file and update the associated paths"""
        old_file_path = Path(self.abs_path)
        new_file_path = old_file_path.parent / new_name

        try:
            old_file_path.rename(new_file_path)  # Perform actual rename operation
            self.current_name = new_name
            self.new_name = new_name
            return True  # Rename was successful
            print(f"[DEBUG] Successfully renamed {self.current_name} → {new_name}")
        except Exception as e:
            print(f"[ERROR] Failed to rename {self.current_name} → {new_name}: {e}")
            return False

        # Update file instance attributes
        self.current_name = new_name
        self.new_name = new_name

    @property
    def parent_id(self) -> str:
        """Return the ID of the parent folder."""
        return self.folder.id if self.folder else None

class DataManager:
    def __init__(self, current_directory: Path):
        self.current_directory = current_directory
        self.data_changed_signal = Signal()
        self.apply_name_signal = Signal()
        self.information_signal = InformationSignal()
        self.root_folder_id = ""
        self.root_folder_path = str(current_directory)

        self.task_execution_signal = Signal()
        self.task_execution_signal.connect(self.on_task_execution)
        
        self.data = {
            "root_path": self.root_folder_path,
            "folders": defaultdict(Folder),
            "summary": {
                "folders_count": 0,
                "enabled_folders_count": 0,
                "files_count": 0,
                "enabled_files_count": 0,
                "total_size": 0,
            }
        }
        self._undo_limit = 50
        self.batch_update_mode = False
        self.undo_stack = deque()
        self.redo_stack = deque()

    def _clone_data(self):
        """Clone current data structure for undo/redo."""
        return deepcopy(self.data)
    
    # Undo/Redo
    def _save_history(self, custom=None):
        print("Im going to save history")
        data_to_append = self._clone_data() if not custom else custom

        if data_to_append is None:
            return
        
        self.redo_stack.clear()
        
        self.undo_stack.append(data_to_append)
        if len(self.undo_stack) > self._undo_limit:  # Limit the history size (adjust as needed)
            self.undo_stack.popleft()
    
    def undo(self):
        if not self.undo_stack:
            print("No undo stack")
            return
        previous_state = self.undo_stack.pop()
        self.redo_stack.append(self._clone_data())
        self.data = previous_state
        self.data_changed_signal.emit({
                "data_type": "undo_done",
                "folders_data": self.data["folders"]
                })
        # self.data_changed_signal.emit({"undo_done": True})
        self.recalculate_summary()

    def redo(self):
        """Redo the last undone change."""
        if not self.redo_stack:
            return  # Nothing to redo
        next_state = self.redo_stack.pop()
        self.undo_stack.append(self._clone_data())  # Save current state to undo stack
        self.data = next_state  # Apply the next state
        self.data_changed_signal.emit({
                "data_type": "redo_done",
                "folders_data": self.data["folders"]
                })
        # self.data_changed_signal.emit({"redo_done": True})
        self.recalculate_summary()  # Recalculate the summary after redo

    def clear_history(self):
        self.undo_stack.clear()
        self.redo_stack.clear()

    def start_batch_update(self):
        """Call this method to start a batch update."""
        self.batch_update_mode = True
        self.data_changed_signal.suppress()

    def end_batch_update(self):
        """Call this method to end a batch update and notify observers."""
        self.batch_update_mode = False
        self.recalculate_summary()
        self.data_changed_signal.resume({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
                })

    # --- Data Getters ---
    def get_pending_changes_count(self) -> int:
        """Return the count of files with pending name changes."""
        pending_changes = 0
        for folder in self.data["folders"].values():
            for file in folder.files:
                if file.new_name != file.current_name:
                    pending_changes += 1
        return pending_changes
    
    def get_pending_folder_changes_count(self) -> int:
        """Return the count of folders with pending name changes."""
        pending_changes = 0
        for folder in self.data["folders"].values():
            if folder.new_name != folder.current_name:
                pending_changes += 1
        return pending_changes

    def get_folder_count(self) -> int:
        """Return the total folder count."""
        return len(self.data["folders"])

    def get_enabled_folder_count(self) -> int:
        """Return the count of enabled folders."""
        return sum(1 for folder in self.data["folders"].values() if folder.is_enabled)

    def get_file_count(self) -> int:
        """Return the total file count across all folders."""
        return sum(len(folder.files) for folder in self.data["folders"].values())

    def get_enabled_file_count(self) -> int:
        """Return the count of enabled files, considering folder enabled state."""
        return sum(1 for folder in self.data["folders"].values() if folder.is_enabled
                for file in folder.files if file.is_enabled)

    def get_total_size(self) -> int:
        """Return the total size of enabled files, considering folder enabled state."""
        return sum(file.size for folder in self.data["folders"].values() if folder.is_enabled
                for file in folder.files if file.is_enabled)

    def get_enabled_file_extensions(self):
        """Return a set of all unique file extensions from enabled folders."""
        file_extensions = set()
        
        for folder_id, folder_data in self.data["folders"].items():
            folder = folder_data  # Assuming folder_data is an instance of Folder
            if not folder.is_enabled:
                continue

            for file in folder.files:
                if not file.is_enabled:
                    continue
                
                file_extensions.add(file.file_ext)
        
        return file_extensions


    # --- Data Setters ---
    def set_folder_enabled(self, folder_id: str, is_enabled: bool) -> None:
        """Enable or disable a folder."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            self._save_history()

            folder.is_enabled = is_enabled
            for file in folder.files:
                file.is_enabled = is_enabled
            
            self.data_changed_signal.emit({
                "data_type": "folder",
                "folder_data": folder,
                "folders_data": self.data["folders"]
            })
            status = "enabled" if is_enabled else "disabled"
            self.information_signal.emit_info(f"Folder {folder.id} has been {status}.", context="folder_enable")
            self.recalculate_summary(updated_data={"folder": folder})
    
    def toggle_folder_enabled(self, folder_id: str) -> None:
        folder = self.data["folders"].get(folder_id)
        folder.is_enabled = not folder.is_enabled
        if folder.is_enabled:
            self.populate_files_for_folder(folder)
        self.data_changed_signal.emit({
                    "data_type": "folder",
                    "folder_data": folder,
                    "folders_data": self.data["folders"]
                })
        status = "enabled" if folder.is_enabled else "disabled"
        self.information_signal.emit_info(f"File {folder.current_name} has been {status}.", context="file_enable")
        self.recalculate_summary(updated_data={"folder": folder})
    
    def toggle_file_enabled(self, folder_id: str, file_id: str) -> None:
        """Toggle the 'is_enabled' status of a specific file within a folder using IDs."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            file_instance = next((f for f in folder.files if f.id == file_id), None)
            if file_instance:
                self._save_history()

                file_instance.is_enabled = not file_instance.is_enabled
                self.data_changed_signal.emit({
                    "data_type": "file",
                    "file_data": file_instance,
                    "folders_data": self.data["folders"]
                })
                status = "enabled" if file_instance.is_enabled else "disabled"
                self.information_signal.emit_info(f"File {file_instance.current_name} has been {status}.", context="file_enable")
                self.recalculate_summary(updated_data={"file": file_instance})


    def set_file_enabled(self, folder_id: str, file_id: str, is_enabled: bool) -> None:
        """Enable or disable a specific file within a folder using IDs."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            file = next((f for f in folder.files if f.id == file_id), None)
            if file:
                self._save_history()
                file.is_enabled = is_enabled  # Update the `is_enabled` attribute directly
                
                self.data_changed_signal.emit({
                    "data_type": "file",
                    "file_data": file,
                    "folders_data": self.data["folders"]
                })
                self.recalculate_summary(updated_data={"file": file})

    def set_folder_name(self, folder_id: str, new_name: str) -> None:
        """Change the name of a file."""
        folder = self.data["folders"].get(folder_id)
        if folder:
                folder.new_name = new_name
                
                self.data_changed_signal.emit({
                    "data_type": "folder",
                    "folder_data": folder,
                    "folders_data": self.data["folders"]
                })
                self.information_signal.emit_info(f"New name: {folder.current_name}")
                self.recalculate_summary(updated_data={"folder": folder})
    
    def set_file_name(self, folder_id: str, file_id: str, new_name: str) -> None:
        """Change the name of a file."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            file_instance = next((f for f in folder.files if f.id == file_id), None)
            if file_instance:
                self._save_history()

                file_instance.new_name = new_name
                
                self.data_changed_signal.emit({
                    "data_type": "file",
                    "file_data": file_instance,
                    "folders_data": self.data["folders"]
                })
                self.information_signal.emit_info(f"New name: {file_instance.current_name}")
                self.recalculate_summary(updated_data={"file": file_instance})
    
    def reset_file_name(self, folder_id: str, file_id: str) -> None:
        """Reset the new name of a specific file to its current name."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            file = next((f for f in folder.files if f.id == file_id), None)
            if file:
                self._save_history()
                # Reset the new name to the current name
                file.new_name = file.current_name
                self.data_changed_signal.emit({
                    "data_type": "file",
                    "file_data": file,
                    "folders_data": self.data["folders"]
                })
                self.information_signal.emit_info(f"Reset name: {file.new_name}")
                self.recalculate_summary(updated_data={"file": file})

    def reset_folder_name(self, folder_id: str) -> None:
        """Change the name of a file."""
        folder = self.data["folders"].get(folder_id)
        if folder:
                folder.new_name = folder.current_name
                
                self.data_changed_signal.emit({
                    "data_type": "folder",
                    "folder_data": folder,
                    "folders_data": self.data["folders"]
                })
                self.information_signal.emit_info(f"Reset name: {folder.new_name}")
                self.recalculate_summary(updated_data={"folder": folder})


    def rename_file(self, folder_id: str, file_id: str, new_name: str) -> None:
        """Emit signal to rename a file."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            file_instance = next((f for f in folder.files if f.id == file_id), None)
            if file_instance:
                if file_instance.rename_file(new_name):
                    self.data_changed_signal.emit({
                        "data_type": "rename_file_done",
                        "file_data": file_instance,
                        "folders_data": self.data["folders"],
                    })
                else:
                    print(f"[ERROR] Rename operation failed for file {file_instance.current_name}")

    def rename_folder(self, folder_id: str, new_name: str) -> None:
        """Emit signal to rename a file."""
        folder = self.data["folders"].get(folder_id)
        if folder:
            if folder.rename_folder(new_name):
                if folder.id == self.root_folder_id:
                    new_root_folder_path = str(Path(self.root_folder_path).parent / new_name)
                    self.root_folder_path = new_root_folder_path
                    folder.root_path = new_root_folder_path
                    folder.update_subfolder_paths()

                self.data_changed_signal.emit({
                    "data_type": "rename_folder_done",
                    "folder_data": folder,
                    "folders_data": self.data["folders"],
                })
            else:
                print(f"[ERROR] Rename operation failed for folder {folder.current_name}")

    def rename_all_files(self, data, option):
        """Rename all files based on the specified option."""
        self.start_batch_update()
        for folder_id, folder_data in data["folders"].items():
            folder = folder_data  # Assuming folder_data is already an instance of Folder
            if not folder.is_enabled and option == "enabled":
                continue

            for file in folder.files:  # Iterating through File objects
                if not file.is_enabled and option == "enabled":
                    continue

                # Directly rename the file by calling the rename_file method
                self.rename_file(folder_id, file.id, file.new_name)
        self.clear_history()
        self.end_batch_update()

    def rename_all_folders(self, data, option):
        """Rename all files based on the specified option."""
        self.start_batch_update()
        for folder_id, folder_data in data["folders"].items():
            folder = folder_data
            if not folder.is_enabled and option == "enabled":
                continue

            self.rename_folder(folder_id, folder.new_name)

        self.clear_history()
        self.end_batch_update()


    def request_apply_names(self, option):
        self.rename_all_files(self.data, option)
        # self.apply_name_signal.emit(self.data, option)

    def process_folder_names(self, process_folder_name_callable: callable, filters: dict = None, state = "file") -> None:
        file_filter = FileFilter(filters)

        initial_state = self._clone_data()
        any_changes = False
        for folder in self.data["folders"].values():
            if not folder.is_enabled:
                continue

            abs_path = folder.folder_path
            folder_name = folder.new_name
            current_name = folder.current_name
            path_obj = Path(abs_path)
            
            if not file_filter.filter(abs_path, folder_name):
                continue

            new_name = process_folder_name_callable(folder_name, path_obj, current_name, state)
            if new_name != folder.new_name:  # Only save history if the name is actually changed
                folder.new_name = new_name
                any_changes = True

        if any_changes:
            self._save_history(custom=initial_state)
            self.data_changed_signal.emit({
                "data_type": "name_processing_done",
                "folders_data": self.data["folders"]
            })
            self.information_signal.emit_info("Processed names")
            self.recalculate_summary()

    def process_file_names(self, process_file_name_callable: callable, filters: dict = None, state = "file") -> None:
        file_filter = FileFilter(filters)

        initial_state = self._clone_data()
        any_changes = False
        for folder in self.data["folders"].values():
            if not folder.is_enabled:
                continue  # Skip disabled folders

            for file in folder.files:
                if not file.is_enabled:
                    continue  # Skip disabled files

                abs_path = file.abs_path
                file_name = file.new_name
                current_name = file.current_name
                path_obj = Path(abs_path)
                if not file_filter.filter(abs_path, file_name):
                    continue  # Skip if the file doesn't pass the filter conditions

                new_name = process_file_name_callable(file_name, path_obj, current_name, state)
                if new_name != file.new_name:  # Only save history if the name is actually changed
                    file.new_name = new_name
                    any_changes = True  # Mark that we have made a change

        if any_changes:
            self._save_history(custom=initial_state)
            self.data_changed_signal.emit({
                "data_type": "name_processing_done",
                "folders_data": self.data["folders"]
            })
            self.information_signal.emit_info("Processed names")
            self.recalculate_summary()


    def reset_all_file_names(self) -> None:
        """Reset all file new names to current names."""
        for folder in self.data["folders"].values():
            for file in folder.files:
                # Reset the new name to the current name
                file.new_name = file.current_name

        self._save_history()
        self.data_changed_signal.emit({
            "data_type": "name_processing_done",
            "folders_data": self.data["folders"]
        })
        self.information_signal.emit_info("Reset names")
        self.recalculate_summary()

    
    def reset_all_folder_names(self) -> None:
        """Reset all file new names to current names."""
        for folder in self.data["folders"].values():
            folder.new_name = folder.current_name

        self._save_history()
        self.data_changed_signal.emit({
            "data_type": "name_processing_done",
            "folders_data": self.data["folders"]
        })
        self.information_signal.emit_info("Reset folder names")
        self.recalculate_summary()


    def update_folder_data(self, node: Any) -> None:
        """Toggle folder and file states based on node status."""
        folder_id = node.data.get("folder_id", "")
        folder = self.data["folders"].get(folder_id)
        if folder:
            self.populate_files_for_folder(folder)
            self._save_history()

            folder.is_enabled = node.is_enabled
            self.data_changed_signal.emit({
                "data_type": "folder",
                "folder_data": folder,
                "folders_data": self.data["folders"]
            })
            self.information_signal.emit_info(f"{node.label.plain.split(' ', 1)[1]} is {node.is_enabled}")
            self.recalculate_summary(updated_data={"folder": folder})


    def recalculate_summary(self, updated_data=None):
        """Recalculate summary data like enabled folder count and total file size."""
        new_summary = self.data["summary"].copy()

        if not updated_data:
            # Full recalculation
            for folder in self.data["folders"].values():
                if folder.is_enabled:
                    new_summary["enabled_folders_count"] += 1
                for file in folder.files:
                    if file.is_enabled:
                        new_summary["enabled_files_count"] += 1
                        new_summary["total_size"] += file.size

        else:
            # Partial update
            if "folder" in updated_data:
                folder = updated_data["folder"]
                if folder.is_enabled:
                    new_summary["enabled_folders_count"] += 1
                else:
                    new_summary["enabled_folders_count"] -= 1

            if "file" in updated_data:
                file = updated_data["file"]
                if file.is_enabled:
                    new_summary["enabled_files_count"] += 1
                    new_summary["total_size"] += file.size
                else:
                    new_summary["enabled_files_count"] -= 1
                    new_summary["total_size"] -= file.size

        if new_summary != self.data["summary"]:
            self.data["summary"] = new_summary
            self.data_changed_signal.emit({
                "data_type": "summary",
                "summary_data": new_summary,
                "folders_data": self.data["folders"]
            })

    def aaapopulate_tree(self, node, path: Path, recursive: bool = True) -> None:
        """Populate the tree iteratively using folder IDs and add files to self.data."""
        stack = [(node, path)]  # Use a stack to avoid recursion

        while stack:
            current_node, current_path = stack.pop()
            folder = self._add_folder(current_path)
            
            is_root = not current_node.data.get("folder_id")
            if is_root:
                current_node.data["folder_id"] = folder.id
                self.root_folder_id = folder.id
                self.populate_files_for_folder(folder)

            total_files = 0

            # Use os.scandir() for faster iteration
            with os.scandir(current_path) as it:
                for entry in it:
                    if entry.is_dir():
                        folder_icon = ENABLED_FOLDER if recursive else DISABLED_FOLDER
                        folder_node = current_node.add(f"{folder_icon} {entry.name}")
                        folder_node.auto_expand = False
                        folder_node.path = Path(entry.path)

                        new_folder = Folder(entry.name, folder, self.root_folder_path)
                        self.data["folders"][new_folder.id] = new_folder

                        new_folder.is_enabled = recursive
                        folder_node.is_enabled = recursive
                        folder_node.data = {
                            "folder_id": new_folder.id
                        }

                        # Instead of recursion, add the folder to the stack
                        stack.append((folder_node, Path(entry.path)))
                        if folder_node.is_enabled:
                            self.populate_files_for_folder(new_folder)

            folder.files_count = total_files  # Store the total file count for this folder

        self.recalculate_summary()

    def populate_tree(self, node, path: Path, recursive: bool = True) -> None:
        """Populate the tree with the root and its immediate children, without recursion."""
        
        is_root = not node.data.get("folder_id")
        folder = self._add_folder(path)

        if is_root:
            node.data["folder_id"] = folder.id
            self.root_folder_id = folder.id
            self.populate_files_for_folder(folder)

        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    folder_icon = DISABLED_FOLDER
                    folder_node = node.add(f"{folder_icon} {entry.name}")
                    folder_node.auto_expand = False
                    folder_node.path = Path(entry.path)

                    new_folder = self._add_folder(folder_node.path)
                    # new_folder = Folder(entry.name, folder, self.root_folder_path)
                    self.data["folders"][new_folder.id] = new_folder

                    new_folder.is_enabled = False
                    folder_node.is_enabled = False
                    folder_node.data = {"folder_id": new_folder.id}

                    # Populate files for the subfolder only if it's enabled
                    if new_folder.is_enabled:
                        self.populate_files_for_folder(new_folder)
            
        folder.subfolders_populated = True
        self.recalculate_summary()


    def populate_files_for_folder(self, folder: Folder = None, folder_id: str = None) -> None:
        """Populate files for a given folder only when it's enabled."""
        if folder is None:
            if folder_id is None:
                raise ValueError("Either 'folder' or 'folder_id' must be provided.")

            folder = self.data.get("folders", {}).get(folder_id)
            if folder is None:
                raise ValueError(f"Folder with ID '{folder_id}' not found.")
            
        if folder.files_populated:
            return

        folder_path = Path(folder.folder_path)

        for file in folder_path.iterdir():
            if file.is_file():
                self._add_file(Path(file))
                # new_file = File(file.name, folder)
                # self.data["folders"][folder.id].files.append(new_file)
                self.data["summary"]["files_count"] += 1
                if folder.is_enabled:
                    self.data["summary"]["enabled_files_count"] += 1

        folder.files_populated = True

    
    def populate_subfolders(self, node, folder: Folder = None, folder_id: str = None) -> None:
        """Populate subfolders and files when folder is expanded."""
        if folder is None:
            if folder_id is None:
                raise ValueError("Either 'folder' or 'folder_id' must be provided.")

            folder = self.data.get("folders", {}).get(folder_id)
            if folder is None:
                raise ValueError(f"Folder with ID '{folder_id}' not found.")
            
        if folder.subfolders_populated:
            if not folder.files_populated:
                self.populate_files_for_folder(folder)
            return
            
        folder_path = Path(folder.folder_path)
        
        if not folder_path.exists() or not folder_path.is_dir():
            return  # Safety check
        
        with os.scandir(folder_path) as it:
            for entry in it:
                if entry.is_dir():
                    folder_icon = DISABLED_FOLDER
                    folder_node = node.add(f"{folder_icon} {entry.name}")
                    folder_node.auto_expand = False
                    folder_node.path = Path(entry.path)

                    new_folder = Folder(entry.name, folder, self.root_folder_path)
                    self.data["folders"][new_folder.id] = new_folder

                    new_folder.is_enabled = False
                    folder_node.is_enabled = False
                    folder_node.data = {"folder_id": new_folder.id}

                    # Populate files for the subfolder when enabled
                    if new_folder.is_enabled:
                        self.populate_files_for_folder(new_folder)

        folder.subfolders_populated = True



    def _add_folder(self, path: Path) -> Folder:
        """Ensure a folder exists in the data structure and return its reference."""
        folder_path = str(path)

        # Check if the folder already exists using its ID
        existing_folder = next((f for f in self.data["folders"].values() if f.folder_path == folder_path), None)

        if existing_folder:
            return existing_folder  # Return the existing folder

        # If folder doesn't exist, create a new one
        parent_folder = next((f for f in self.data["folders"].values() if f.folder_path == str(path.parent)), None)
        folder = Folder(folder_name=path.name, parent=parent_folder, root_path=self.root_folder_path)

        if parent_folder:
            parent_folder.add_folder(folder)

        # Store the folder using its ID instead of folder_path
        self.data["folders"][folder.id] = folder
        
        return folder


    def _add_file(self, file: Path) -> None:
        """Add a file to its parent folder in the data structure."""
        parent_folder = self._add_folder(file.parent)
        file_instance = File(file_name=file.name, folder=parent_folder)
        parent_folder.files.append(file_instance)

    def get_enabled_folders(self, node):
        """Retrieve all enabled folders in the tree."""
        enabled_folders = []
        if node.is_enabled:
            enabled_folders.append(node)
        for child in node.children:
            enabled_folders.extend(self.get_enabled_folders(child))
        return enabled_folders

    def is_folder_enabled(self, file_abs_path: str) -> bool:
        """Check if the folder containing the given file is enabled."""
        folder_path = str(Path(file_abs_path).parent)
        folder = self.data["folders"].get(folder_path)
        if folder is None:
            return False
        return folder.is_enabled

    
    def enable_all_folders(self, is_enabled: bool) -> None:
        """Enable or disable all files across all folders."""
        any_changes = False
        for folder in self.data["folders"].values():
            
            current_state = folder.is_enabled
            if current_state == is_enabled:
                continue

            folder.is_enabled = is_enabled
            any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()

    def enable_all_files(self, is_enabled: bool) -> None:
        """Enable or disable all files across all folders."""
        any_changes = False
        for folder in self.data["folders"].values():
            if not folder.is_enabled:
                continue  # Skip disabled folders
            
            for file in folder.files:
                # Explicitly update the 'is_enabled' value to the desired state
                current_state = file.is_enabled
                if current_state == is_enabled:
                    continue

                # Enable/Disable the file
                file.is_enabled = is_enabled
                any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()

    
    def enable_files_by_ext(self, extension: str, is_enabled: bool, isolate: bool = False) -> None:
        """Enable or disable all files with a specific extension."""
        any_changes = False
        for folder in self.data["folders"].values():
            if not folder.is_enabled:
                continue  # Skip disabled folders
            
            for file in folder.files:
                if isolate:
                    file.is_enabled = False
                # if file.is_enabled == is_enabled:
                #     continue
                
                if file.new_name.endswith(f".{extension}"):
                    file.is_enabled = is_enabled
                    any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()


    def enable_files_by_pattern(self, pattern: str, is_enabled: bool) -> None:
        """Enable or disable all files matching a wildcard pattern."""
        pattern = pattern.replace("*", ".*")  # Convert wildcard to regex
        regex = re.compile(pattern)
        any_changes = False
        
        for folder in self.data["folders"].values():
            if not folder.is_enabled:
                continue  # Skip disabled folders
            
            for file in folder.files:
                if file.is_enabled == is_enabled:
                    continue  # Skip if already in the desired state
                
                if regex.fullmatch(file.new_name):
                    file.is_enabled = is_enabled
                    any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()
    
    def enable_folders_by_pattern(self, pattern: str, is_enabled: bool) -> None:
        """Enable or disable all files matching a wildcard pattern."""
        pattern = pattern.replace("*", ".*")  # Convert wildcard to regex
        regex = re.compile(pattern)
        any_changes = False
        
        for folder in self.data["folders"].values():
            if regex.fullmatch(folder.new_name):
                folder.is_enabled = is_enabled
                any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()


    def enable_files_by_regex(self, regex_pattern: str, is_enabled: bool) -> None:
        """Enable or disable all files matching a regex pattern."""
        try:
            regex = re.compile(regex_pattern)
        except re.error:
            print(f"Invalid regex: {regex_pattern}")
            return
        
        any_changes = False
        
        for folder in self.data["folders"].values():
            if not folder.is_enabled:
                continue  # Skip disabled folders
            
            for file in folder.files:
                if file.is_enabled == is_enabled:
                    continue  # Skip if already in the desired state
                
                if regex.fullmatch(file.new_name):
                    file.is_enabled = is_enabled
                    any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()

    def enable_folders_by_regex(self, regex_pattern: str, is_enabled: bool) -> None:
        """Enable or disable all files matching a regex pattern."""
        try:
            regex = re.compile(regex_pattern)
        except re.error:
            print(f"Invalid regex: {regex_pattern}")
            return
        
        any_changes = False
        
        for folder in self.data["folders"].values():
            if regex.fullmatch(folder.new_name):
                folder.is_enabled = is_enabled
                any_changes = True
        
        if any_changes:
            self.data_changed_signal.emit({
                "data_type": "batch_update_done",
                "folders_data": self.data["folders"]
            })
            self.recalculate_summary()


    def on_task_execution(self, data):
        """Handle task execution based on the signal received."""
        task_type = data["type"]
        state = data["state"]

        if task_type == "enable-all":
            if state == "file":
                self.enable_all_files(True)
            elif state == "folder":
                self.enable_all_folders(True)

        elif task_type == "disable-all":
            if state == "file":
                self.enable_all_files(False)
            elif state == "folder":
                self.enable_all_folders(False)

        elif task_type == "reset-all":
            if state == "file":
                self.reset_all_file_names()
            elif state == "folder":
                self.reset_all_folder_names()

        elif task_type == "enable-pattern":
            pattern = data["pattern"]
            if state == "file":
                self.enable_files_by_pattern(pattern, True)
            elif state == "folder":
                self.enable_folders_by_pattern(pattern, True)
        elif task_type == "disable-pattern":
            pattern = data["pattern"]
            if state == "file":
                self.enable_files_by_pattern(pattern, False)
            elif state == "folder":
                self.enable_folders_by_pattern(pattern, False)

        elif task_type == "enable-regex":
            regex = data["regex"]
            if state == "file":
                self.enable_files_by_regex(regex, True)
            elif state == "folder":
                self.enable_folders_by_regex(regex, True)
        elif task_type == "disable-regex":
            regex = data["regex"]
            if state == "file":
                self.enable_files_by_regex(regex, False)
            elif state == "folder":
                self.enable_folders_by_regex(regex, False)

        elif task_type == "enable-ext":
            ext = data["extension"]
            if state == "file":
                self.enable_files_by_ext(ext, True)
        elif task_type == "disable-ext":
            ext = data["extension"]
            if state == "file":
                self.enable_files_by_ext(ext, False)

        elif task_type == "request_apply_names":
            scope = data["scope"]
            if state == "file":
                self.rename_all_files(self.data, scope)
            elif state == "folder":
                self.rename_all_folders(self.data, scope)

        elif task_type == "process-file-names":
            filters = data["filters"]
            pipeline = data["pipeline"]
            if state == "file":
                self.process_file_names(pipeline, filters, state)
            elif state == "folder":
                self.process_folder_names(pipeline, filters, state)

        elif task_type == "rename-file":
            self.rename_file(folder_id=data["folder_id"], file_id=data["file_id"], new_name=data["new_name"])
        elif task_type == "rename-folder":
            self.rename_folder(folder_id=data["folder_id"], new_name=data["new_name"])
        elif task_type == "reset-file-name":
            self.reset_file_name(folder_id=data["folder_id"], file_id=data["file_id"])
        elif task_type == "reset-folder-name":
            self.reset_folder_name(folder_id=data["folder_id"])
        elif task_type == "toggle-file":
            self.toggle_file_enabled(folder_id=data["folder_id"], file_id=data["file_id"])
        elif task_type == "toggle-folder":
            self.toggle_folder_enabled(folder_id=data["folder_id"])