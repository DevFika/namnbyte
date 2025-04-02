from .file_renamer import FileRenamer

# TODO: Decouple
class SignalConnector:
    def __init__(self, data_manager, file_table, folder_table, info_display, output_display, toggle_tree, command_pipeline_handler):
        self.data_manager = data_manager
        self.file_table = file_table
        self.folder_table = folder_table
        self.info_display = info_display
        self.output_display = output_display
        self.toggle_tree = toggle_tree
        self.command_pipeline_handler = command_pipeline_handler
        self.emit_display_data()

    def connect_signals(self):
        """Connect all signals to their handlers."""
        self.data_manager.data_changed_signal.connect(self.on_data_changed)
        self.data_manager.information_signal.connect(self.output_display.information_signal.emit)
        self.command_pipeline_handler.information_signal.connect(self.output_display.information_signal.emit)
        self.command_pipeline_handler.task_request_signal.connect(self.data_manager.task_execution_signal.emit)
        self.file_table.task_request_signal.connect(self.data_manager.task_execution_signal.emit)
        self.folder_table.task_request_signal.connect(self.data_manager.task_execution_signal.emit)

    def on_data_changed(self, updated_data):
        """Handle updates from the DataManager."""
        data_type = updated_data["data_type"]
        folders_data = updated_data["folders_data"]
        if data_type == "folder":
            folder_data = updated_data["folder_data"]
            self.file_table.update_table.emit(folders_data, update_type="folders_data")
            self.folder_table.update_table.emit(folder_data, update_type="folder_data")
            self.toggle_tree.refresh_nodes_signal.emit()
        elif data_type == "file":
            file_data = updated_data["file_data"]
            self.file_table.update_table.emit(file_data, update_type="file_data")
        elif data_type == "summary":
            self.emit_display_data()
        elif data_type == "batch_update_done":
            self.file_table.update_table.emit(folders_data, update_type="folders_data")
            self.folder_table.update_table.emit(folders_data, update_type="folders_data")
            self.toggle_tree.refresh_nodes_signal.emit()
            self.emit_display_data()
        elif data_type == "name_processing_done":
            self.file_table.update_table.emit(folders_data, update_type="folders_data")
            self.folder_table.update_table.emit(folders_data, update_type="folders_data")
            self.toggle_tree.refresh_nodes_signal.emit()
        elif data_type == "undo_done":
            self.file_table.update_table.emit(folders_data, update_type="folders_data")
            self.folder_table.update_table.emit(folders_data, update_type="folders_data")
            self.toggle_tree.refresh_nodes_signal.emit()
            self.output_display.information_signal.emit({
                "message": f"Undo Successful",
                "type": "success",
                "context": "undo"
            })
        elif data_type == "redo_done":
            self.file_table.update_table.emit(folders_data, update_type="folders_data")
            self.folder_table.update_table.emit(folders_data, update_type="folders_data")
            self.toggle_tree.refresh_nodes_signal.emit()
            self.output_display.information_signal.emit({
                "message": f"Redo Successful",
                "type": "success",
                "context": "redo"
            })
        elif data_type == "rename_file_done":
            self.data_manager.clear_history()
            self.emit_display_data()
            file_data = updated_data["file_data"]
            self.file_table.update_table.emit(file_data, update_type="file_data")
            self.output_display.information_signal.emit({
                "message": f"Rename Successful",
                "type": "success",
                "context": "file_rename"
            })
        elif data_type == "rename_folder_done":
            self.data_manager.clear_history()
            self.emit_display_data()
            self.folder_table.update_table.emit(folders_data, update_type="folders_data")
            self.toggle_tree.refresh_nodes_signal.emit()
            self.output_display.information_signal.emit({
                "message": f"Rename Successful",
                "type": "success",
                "context": "folder_rename"
            })
        

    def emit_display_data(self):
        amount_of_folders = self.data_manager.get_folder_count()
        amount_of_enabled_folders = self.data_manager.get_enabled_folder_count()
        amount_of_files = self.data_manager.get_file_count()
        amount_of_enabled_files = self.data_manager.get_enabled_file_count()
        undo_stack = self.data_manager.undo_stack
        redo_stack = self.data_manager.redo_stack
        pending_changes_count = self.data_manager.get_pending_changes_count()
        pending_folder_changes_count = self.data_manager.get_pending_folder_changes_count()
        display_data = {
            "amount_of_folders": amount_of_folders,
            "amount_of_enabled_folders": amount_of_enabled_folders,
            "amount_of_files": amount_of_files,
            "amount_of_enabled_files": amount_of_enabled_files,
            "undo_stack": undo_stack,
            "redo_stack": redo_stack,
            "pending_changes_count": pending_changes_count,
            "pending_folder_changes_count": pending_folder_changes_count
        }
        self.info_display.refresh_display_signal.emit(display_data)