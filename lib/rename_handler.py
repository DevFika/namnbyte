from .file_renamer import FileRenamer

class RenameHandler:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.data_manager.data_changed_signal.connect(self.on_data_changed)

    def on_data_changed(self, updated_data):
        if "rename_signal" in updated_data:
            rename_data = updated_data["rename_signal"]
            self.handle_rename(rename_data)

    def handle_rename(self, rename_data):
        folder_path = rename_data["folder_path"]
        old_name = rename_data["old_name"]
        new_name = rename_data["new_name"]

        folder_data = self.data_manager.data["folders"].get(folder_path)
        if not folder_data:
            return

        file_data = next((f for f in folder_data["files"] if f["name"] == old_name), None)
        if not file_data:
            return

        try:
            FileRenamer.rename_file(folder_path, old_name, new_name, file_data)
            self.data_manager.data_changed_signal.emit({"file": file_data, "rename_done": True})
        except Exception as e:
            print(f"Error renaming file: {e}")