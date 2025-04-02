from textual.widgets import DataTable, Input, RichLog, Select
from textual.screen import ModalScreen, Screen
from textual.events import Click
from textual.app import ComposeResult
from textual import on
from lib import DataManager
from typing import Any
from rich.text import Text
import difflib

from .signal import Signal
from .columns import FileTableColumns

def highlight_changes(original, new):
    """Highlight differences between original and new name using rich.Text."""
    matcher = difflib.SequenceMatcher(None, original, new)
    
    highlighted_original = Text()
    highlighted_new = Text()

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            highlighted_original.append(original[i1:i2], style="dim")
            highlighted_new.append(new[j1:j2])
        elif tag == "replace" or tag == "insert":
            highlighted_new.append(new[j1:j2], style="green")
            highlighted_original.append(original[i1:i2], style="red")
        elif tag == "delete":
            highlighted_original.append(original[i1:i2], style="red")

    return highlighted_original, highlighted_new

class FileTable(DataTable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_request_signal = Signal()
        self.update_table = Signal()
        self.update_table.connect(self.on_update_table)
        self.row_metadata = {}
        self.column_sort_order = {}
        self.column_mapping = FileTableColumns.get_all_columns()
        self.loading = True
        self.initialize_table()

    def get_column_index_by_key(self, column_key):
        """Helper function to get column index by key using the Enum."""
        return FileTableColumns.get_column_index(self.column_mapping, column_key)

    def get_column_name_by_key(self, column_key):
        """Helper function to get column name by key using the Enum."""
        return FileTableColumns.get_column_name(column_key)

    @on(DataTable.CellSelected)
    def data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        # Extracting the cell value
        cell_value = event.value
        selected_column_index = event.coordinate.column
        message = (
            f"Original value of cell at {event.coordinate}"
            f" is {event.value} and type {type(event.value)}"
        )

        is_enabled_index = self.get_column_index_by_key(FileTableColumns.IS_ENABLED.value["key"])
        current_name_index = self.get_column_index_by_key(FileTableColumns.CURRENT_NAME.value["key"])
        new_name_index = self.get_column_index_by_key(FileTableColumns.NEW_NAME.value["key"])
        folder_path_column_index = self.get_column_index_by_key(FileTableColumns.FOLDER_PATH.value["key"])
        reset_index = self.get_column_index_by_key(FileTableColumns.RESET.value["key"])
        apply_index = self.get_column_index_by_key(FileTableColumns.APPLY.value["key"])
        id_index = self.get_column_index_by_key(FileTableColumns.ID.value["key"])
        pid_index = self.get_column_index_by_key(FileTableColumns.PID.value["key"])

        current_row = event.coordinate.row

        is_enabled_value = self.get_cell_at((current_row, is_enabled_index))
        current_name_value = self.get_cell_at((current_row, current_name_index))
        folder_value = self.get_cell_at((current_row, folder_path_column_index))
        new_name_value = self.get_cell_at((current_row, new_name_index))
        id_value = self.get_cell_at((current_row, id_index))
        pid_value = self.get_cell_at((current_row, pid_index))
        if isinstance(folder_value, Text):
            folder_value = folder_value.plain
        if isinstance(current_name_value, Text):
            current_name_value = current_name_value.plain
        if isinstance(new_name_value, Text):
            new_name_value = new_name_value.plain
        if isinstance(is_enabled_value, Text):
            is_enabled_value = is_enabled_value.plain
        if isinstance(cell_value, Text):
            cell_value = cell_value.plain
        if isinstance(id_value, Text):
            id_value = id_value.plain
        if isinstance(pid_value, Text):
            pid_value = pid_value.plain

        if selected_column_index == is_enabled_index:
            self.task_request_signal.emit({
                "type": "toggle-file",
                "state": "file",
                "folder": folder_value,
                "folder_id": pid_value,
                "file_id": id_value,
            })

            print("Lets toggle file")
        elif selected_column_index == new_name_index:
            print("Lets push edit cell")
            self.post_message(EditCellRequested(self, current_row, selected_column_index, cell_value, table_type="file"))
        elif selected_column_index == reset_index:
            self.task_request_signal.emit({
                "type": "reset-file-name",
                "state": "file",
                "folder": folder_value,
                "folder_id": pid_value,
                "file_id": id_value,
                "current_name": current_name_value,
                "new_name": new_name_value
            })

        elif selected_column_index == apply_index:
            self.task_request_signal.emit({
                "type": "rename-file",
                "state": "file",
                "folder": folder_value,
                "folder_id": pid_value,
                "file_id": id_value,
                "current_name": current_name_value,
                "new_name": new_name_value
            })

    def initialize_table(self):
        self.clear()
        for index, column in enumerate(self.column_mapping):
            self.add_column(column["name"], key=str(index))

    def populate_table(self, folder_data):
        self.loading = True
        self.clear()
        for folder in folder_data.values():
            if not folder.is_enabled:
                continue
            # if not folder["is_enabled"]:
            for file_data in folder.files:
                print(file_data)
                self.add_file_row(file_data)
        
        self.loading = False

    def add_file_row(self, file_data):
        # Create a list to store the row, applying highlight changes to current_name and new_name
        row = []

        # Iterate through each column in the column mapping
        for column in self.column_mapping:
            # Get the value for the current column using the new method
            value = self.get_file_data(file_data, column["key"])

            # If the column is either current_name or new_name, apply highlighting
            if column["key"] == "current_name":
                original_name = file_data.current_name
                new_name = file_data.new_name
                highlighted_current, _ = highlight_changes(original_name, new_name)
                row.append(highlighted_current)  # Add the highlighted current name
            elif column["key"] == "new_name":
                original_name = file_data.current_name
                new_name = file_data.new_name
                _, highlighted_new = highlight_changes(original_name, new_name)
                row.append(highlighted_new)  # Add the highlighted new name
            else:
                row.append(value if isinstance(value, Text) else Text(str(value), style="dim"))

        # Apply additional classes for styling if necessary
        classes = []
        if not file_data.is_enabled:
            classes.append("disabled")
        if file_data.current_name != file_data.new_name:
            classes.append("pending-change")

        # Add the row to the table with the appropriate classes
        self.add_row(*row, key=file_data.id)



    def update_file_row(self, file_data):
        """Update a file row with highlighted changes for current_name and new_name."""
        rel_path = file_data.rel_path
        file_id = file_data.id
        print(rel_path)
        print(rel_path)
        print(rel_path)

        if file_id not in self.rows:
            print("No file id in data")
            return

        # Iterate over each column to update the relevant cells
        for column_index, column in enumerate(self.column_mapping):
            value = self.get_file_data(file_data, column["key"])
            print(value)

            # Apply highlighting to the columns that have current_name or new_name
            if column["key"] == "current_name":
                original_name = file_data.current_name
                new_name = file_data.new_name
                highlighted_current, _ = highlight_changes(original_name, new_name)
                # Use update_cell to update the current_name cell with highlighted text
                self.update_cell(file_id, str(column_index), highlighted_current)
            
            elif column["key"] == "new_name":
                original_name = file_data.current_name
                new_name = file_data.new_name
                _, highlighted_new = highlight_changes(original_name, new_name)
                # Use update_cell to update the new_name cell with highlighted text
                self.update_cell(file_id, str(column_index), highlighted_new)
            
            else:
                # For other columns, update the cell without highlighting
                self.update_cell(file_id, str(column_index), value if isinstance(value, Text) else Text(str(value), style="dim"))


    def remove_file_row(self, rel_path: str):
        if rel_path in self.rows:
            self.remove_row(rel_path)

    def handle_file_rename(self, old_rel_path: str, file_data: dict):
        self.remove_file_row(old_rel_path)
        self.add_file_row(file_data)

    def get_file_data(self, file_data, key):
        # Access the key from the Enum
        if key == FileTableColumns.IS_ENABLED.value["key"]:
            # Use green for enabled (✓) and red for disabled (✗)
            return Text("✓", style="bold #A3BE8C") if file_data.is_enabled else Text("✗", style="bold #BF616A")
        
        if key == FileTableColumns.RESET.value["key"]:
            is_pending = file_data.current_name != file_data.new_name
            # Use bright cyan for reset icon (↻)
            return Text("↻", style="bold #EBCB8B") if is_pending else Text(" ")
        
        if key == FileTableColumns.APPLY.value["key"]:
            is_pending = file_data.current_name != file_data.new_name
            # Use bright yellow for apply icon (⏎)
            return Text("⏎", style="bold #88C0D0") if is_pending else Text(" ")
        
        # For other keys, access the file's attributes directly
        if hasattr(file_data, key):
            return getattr(file_data, key, "")
        
        return ""  # Default case if no matching attribute is found

    def update(self, updated_data):
        if "file" in updated_data and "old_name" in updated_data and "new_name" in updated_data:
            file_data = updated_data["file"]
            old_rel_path = updated_data["file"]["rel_path"].replace(file_data["new_name"], updated_data["old_name"])
            self.handle_file_rename(old_rel_path, file_data)
        elif "file" in updated_data:
            self.update_file_row(updated_data["file"])

    def sort_by_column(self, column_index: int):
        """Generic sort handler for any column by index, not by key."""
        def get_sort_key(value):
            real_value = value
            if isinstance(value, Text):
                real_value = value.plain
            # Optional: Custom sort for "is_enabled" column
            # if column_index == 0:  # Column 0 is "is_enabled"
            #     return value == "✅"  # ✅ = True, ❌ = False
            return real_value

        reverse = self.column_sort_order.get(column_index, False)
        self.column_sort_order[column_index] = not reverse

        self.sort(str(column_index), key=get_sort_key, reverse=reverse)


    @on(DataTable.HeaderSelected)
    def on_header_selected(self, event: DataTable.HeaderSelected) -> None:
        """Sort the table when the user clicks a column header."""
        self.sort_by_column(event.column_index)

    def get_column_index_by_key(self, key: str) -> int | None:
        """Helper to get column index by column key."""
        for index, column in enumerate(self.column_mapping):
            if column["key"] == key:
                return index
        return None
    
    def on_update_table(self, data, update_type, *args, **kwargs) -> None:
        if update_type == "folders_data":
            self.populate_table(data)
        elif update_type == "file_data":
            self.update_file_row(data)

from textual.message import Message

class EditCellRequested(Message):
    def __init__(self, sender: FileTable, row: int, column: int, value: str, table_type: str):
        super().__init__()
        self.sender = sender
        self.row = row
        self.column = column
        self.value = value
        self.table_type = table_type