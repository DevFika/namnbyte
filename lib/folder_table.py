from textual.widgets import DataTable
from textual import on
from rich.text import Text
from .signal import Signal
from .columns import FolderTableColumns  # Assuming FolderTableColumns exist similar to FileTableColumns
from .file_table import EditCellRequested, highlight_changes
class FolderTable(DataTable):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_request_signal = Signal()
        self.update_table = Signal()
        self.update_table.connect(self.on_update_table)
        self.row_metadata = {}
        self.column_sort_order = {}
        # self.column_mapping = FolderTableColumns.get_all_columns()  # Assuming FolderTableColumns is structured similarly to FileTableColumns
        self.loading = True
        self.initialize_table()

    def get_column_index_by_key(self, column_key):
        """Helper function to get column index by key using the Enum."""
        return FolderTableColumns.get_column_index(self.column_mapping, column_key)

    def get_column_name_by_key(self, column_key):
        """Helper function to get column name by key using the Enum."""
        return FolderTableColumns.get_column_name(column_key)

    @on(DataTable.CellSelected)
    def data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        # Extracting the cell value
        cell_value = event.value
        current_row = event.coordinate.row
        selected_column_index = event.coordinate.column
        selected_column_key = self.get_column_key_by_index(event.coordinate.column)  # Get key instead of index
        print(f"selected_column_key {selected_column_key}\n"*50)
        # message = (
        #     f"Original value of cell at {event.coordinate} "
        #     f"is {event.value} and type {type(event.value)}"
        # )

        # rel_path_column_index = self.get_column_index_by_key(FolderTableColumns.REL_PATH.value["key"])
        # is_enabled_index = self.get_column_index_by_key(FolderTableColumns.IS_ENABLED.value["key"])
        current_name_index = self.get_column_index_by_key(FolderTableColumns.CURRENT_NAME.value["key"])
        new_name_index = self.get_column_index_by_key(FolderTableColumns.NEW_NAME.value["key"])
        folder_path_column_index = self.get_column_index_by_key(FolderTableColumns.FOLDER_PATH.value["key"])
        # reset_index = self.get_column_index_by_key(FolderTableColumns.RESET.value["key"])
        # apply_index = self.get_column_index_by_key(FolderTableColumns.APPLY.value["key"])
        id_index = self.get_column_index_by_key(FolderTableColumns.ID.value["key"])

        # rel_path_value = self.text_to_plain(self.get_cell_at((current_row, rel_path_column_index)))
        # is_enabled_value = self.text_to_plain(self.get_cell_at((current_row, is_enabled_index)))
        current_name_value = self.text_to_plain(self.get_cell_at((current_row, current_name_index)))
        folder_value = self.text_to_plain(self.get_cell_at((current_row, folder_path_column_index)))
        # reset_value = self.text_to_plain(self.get_cell_at((current_row, reset_index)))
        new_name_value = self.text_to_plain(self.get_cell_at((current_row, new_name_index)))
        id_value = self.text_to_plain(self.get_cell_at((current_row, id_index)))

        current_row = event.coordinate.row

        if selected_column_key == FolderTableColumns.NEW_NAME.value["key"]:
            self.post_message(EditCellRequested(self, current_row, selected_column_index, cell_value, table_type="folder"))
        if selected_column_key == FolderTableColumns.CURRENT_NAME.value["key"]:
            pass

        elif selected_column_key == FolderTableColumns.IS_ENABLED.value["key"]:
            self.task_request_signal.emit({
                "type": "toggle-folder",
                "state": "folder",
                "folder": folder_value,
                "folder_id": id_value,
                "current_name": current_name_value,
                "new_name": new_name_value
            })

        elif selected_column_key == FolderTableColumns.FOLDER_PATH.value["key"]:
            print(f"User clicked on 'Folder Path' in row {current_row}\n"*50)

        elif selected_column_key == FolderTableColumns.RESET.value["key"]:
            self.task_request_signal.emit({
                "type": "reset-folder-name",
                "state": "folder",
                "folder": folder_value,
                "folder_id": id_value,
                "current_name": current_name_value,
                "new_name": new_name_value
            })

        elif selected_column_key == FolderTableColumns.APPLY.value["key"]:
            self.task_request_signal.emit({
                "type": "rename-folder",
                "state": "folder",
                "folder": folder_value,
                "folder_id": id_value,
                "current_name": current_name_value,
                "new_name": new_name_value
            })


    def initialize_table(self):
        self.loading = True
        self.clear()
        self.column_mapping = {}
        for column in FolderTableColumns:
            column_key = column.value["key"]
            self.add_column(column.value["name"], key=column_key)  # Use column key instead of index
            self.column_mapping[column_key] = column  # Store mapping of key to Enum
        
        self.loading = False

    def populate_table(self, folder_data):
        self.clear()
        for folder in folder_data.values():
            # if not folder.is_enabled:
            #     continue
            self.add_folder_row(folder)

    def get_column_key_by_index(self, column_index):
        """Retrieve the column key using its index."""
        column_keys = list(self.column_mapping.keys())  # Get ordered list of column keys
        if 0 <= column_index < len(column_keys):
            return column_keys[column_index]
        return None  # Return None if index is out of range


    def add_folder_row(self, folder_data):
        row = []

        for column in self.column_mapping.values():  # Iterate over Enum values
            column_key = column.value["key"]
            value = self.get_folder_data(folder_data, column_key)

            # Apply highlighting if needed
            if column_key == "current_name":
                original_name = folder_data.current_name
                new_name = folder_data.new_name
                highlighted_current, _ = highlight_changes(original_name, new_name)
                row.append(highlighted_current)
            elif column_key == "new_name":
                original_name = folder_data.current_name
                new_name = folder_data.new_name
                _, highlighted_new = highlight_changes(original_name, new_name)
                row.append(highlighted_new)
            else:
                row.append(value if isinstance(value, Text) else Text(str(value), style="dim"))

        # Set row classes
        classes = []
        if not folder_data.is_enabled:
            classes.append("disabled")
        if folder_data.current_name != folder_data.new_name:
            classes.append("pending-change")

        self.add_row(*row, key=folder_data.id)


    def update_folder_row(self, folder_data):
        folder_id = folder_data.id
        if folder_id not in self.rows:
            print("No folder id in data")
            return

        # Iterate over each column and update the respective cells
        for column_index, column in enumerate(self.column_mapping.values()):
            column_key = column.value["key"]
            value = self.get_folder_data(folder_data, column_key)

            # Apply highlighting for the "current_name" and "new_name" columns
            if column_key == "current_name":
                original_name = folder_data.current_name
                new_name = folder_data.new_name
                highlighted_current, _ = highlight_changes(original_name, new_name)
                # Update the cell with highlighted text for current_name
                self.update_cell(folder_id, column_key, highlighted_current)
            elif column_key == "new_name":
                original_name = folder_data.current_name
                new_name = folder_data.new_name
                _, highlighted_new = highlight_changes(original_name, new_name)
                # Update the cell with highlighted text for new_name
                self.update_cell(folder_id, column_key, highlighted_new)
            else:
                # For other columns, update the cell normally
                self.update_cell(folder_id, column_key, value if isinstance(value, Text) else Text(str(value), style="dim"))

        # Apply classes for styling (e.g., disabled, pending-change)
        # classes = []
        # if not folder_data.is_enabled:
        #     classes.append("disabled")
        # if folder_data.current_name != folder_data.new_name:
        #     classes.append("pending-change")

        # # Now apply the classes to the row by updating the row's classes
        # self.update_row_classes(folder_id, classes)

    def remove_folder_row(self, folder_id: str):
        if folder_id in self.rows:
            self.remove_row(folder_id)

    def handle_folder_rename(self, old_folder_id: str, folder_data: dict):
        self.remove_folder_row(old_folder_id)
        self.add_folder_row(folder_data)

    def get_folder_data(self, folder_data, key):
        if key == FolderTableColumns.IS_ENABLED.value["key"]:
            return Text("✓", style="bold #A3BE8C") if folder_data.is_enabled else Text("✗", style="bold #BF616A")
        
        if key == FolderTableColumns.RESET.value["key"]:
            return Text("↻", style="bold #EBCB8B") if folder_data.current_name != folder_data.new_name else Text(" ")

        if key == FolderTableColumns.APPLY.value["key"]:
            return Text("⏎", style="bold #88C0D0") if folder_data.current_name != folder_data.new_name else Text(" ")

        if hasattr(folder_data, key):
            return getattr(folder_data, key, "")

        return ""

    def update(self, updated_data):
        if "folder" in updated_data and "old_name" in updated_data and "new_name" in updated_data:
            folder_data = updated_data["folder"]
            old_folder_id = updated_data["folder"]["id"].replace(folder_data["new_name"], updated_data["old_folder_name"])
            self.handle_folder_rename(old_folder_id, folder_data)
        elif "folder" in updated_data:
            self.update_folder_row(updated_data["folder"])

    def sort_by_column(self, column_key: str):
        def get_sort_key(value):
            real_value = value
            if isinstance(value, Text):
                real_value = value.plain
            return real_value

        reverse = self.column_sort_order.get(column_key, False)
        self.column_sort_order[column_key] = not reverse

        self.sort(column_key, key=get_sort_key, reverse=reverse)  # Sort by key, not index

    def text_to_plain(self, text):
        if isinstance(text, Text):
            plain = text.plain
            return plain
        return text


    @on(DataTable.HeaderSelected)
    def on_header_selected(self, event: DataTable.HeaderSelected) -> None:
        column_key = self.get_column_key_by_index(event.column_index)
        if column_key:
            self.sort_by_column(column_key)

    def get_column_index_by_key(self, key: str) -> int | None:
        for index, column in enumerate(self.column_mapping.values()):  # Iterate over Enum values
            if column.value["key"] == key:
                return index
        return None


    def on_update_table(self, data, update_type, *args, **kwargs) -> None:
        if update_type == "folders_data":
            self.populate_table(data)
        elif update_type == "folder_data":
            self.update_folder_row(data)

