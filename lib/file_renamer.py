from pathlib import Path
from .signal import Signal
class FileRenamer:

    @staticmethod
    def rename_file(folder_path: str, old_name: str, new_name: str, file_instance) -> None:
        old_file_path = Path(file_instance.abs_path)
        new_file_path = old_file_path.parent / new_name

        print(f"[DEBUG] Attempting to rename file:")
        print(f"        Old Path: {old_file_path}")
        print(f"        New Path: {new_file_path}")

        try:
            old_file_path.rename(new_file_path)  # Perform actual rename operation
            print(f"[DEBUG] Successfully renamed {old_name} → {new_name}")
        except Exception as e:
            print(f"[ERROR] Failed to rename {old_name} → {new_name}: {e}")
            return  # Exit early if renaming failed

        # Update file instance attributes
        old_rel_path = file_instance.rel_path
        file_instance.current_name = new_name
        file_instance.new_name = new_name
        file_instance._update_paths()

        print(f"[DEBUG] Updated file instance attributes:")
        print(f"        Current Name: {file_instance.current_name}")
        print(f"        New Name: {file_instance.new_name}")
        print(f"        Absolute Path: {file_instance.abs_path}")
        print(f"        Relative Path (old → new): {old_rel_path} → {file_instance.rel_path}")