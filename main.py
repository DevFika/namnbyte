import os, sys
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Static, Button, Footer, DataTable, Placeholder, Input, TabbedContent, TabPane, LoadingIndicator
from pathlib import Path
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer, Grid
from rich.text import Text
from textual.widgets import MarkdownViewer

from lib import DataManager, ToggleTree, InfoDisplay, OutputDisplay, FileTable, EditCellRequested
from lib import FileTableColumns, FolderTableColumns, EditCellScreen, process_names, CommandSuggester, CommandPipelineHandler
from lib import SignalConnector, FolderTable, FlexSplitHorizontal, FlexSplitVertical, generate_markdown, generate_readme_markdown
ENABLED_FOLDER = f"[#A3BE8C]✓[/#A3BE8C]"
class Namnbyte(App[None]):
    BINDINGS = [
        Binding("1", "focus_tree", "Focus on Tree View", show=True),
        Binding("f1", "focus_tree", "Focus on Tree View", show=False),
        Binding("2", "focus_data_table", "Focus on Data Table", show=True),
        Binding("f2", "focus_data_table", "Focus on Data Table", show=False),
        Binding("3", "focus_folder_table", "Focus on Folder Table", show=True),
        Binding("f3", "focus_folder_table", "Focus on Folder Table", show=False),
        Binding("4", "focus_input", "Focus on Input Field", show=True),
        Binding("f4", "focus_input", "Focus on Input Field", show=False),
        Binding("ctrl+z", "undo", "Undo Action", show=True),
        Binding("ctrl+y", "redo", "Redo Action", show=True),
        Binding("up", "history_up", "Previous Command", show=True),
        Binding("down", "history_down", "Next Command", show=True),
    ]

    CSS_PATH = "lib/assets/main.tcss"
    ENABLE_COMMAND_PALETTE = False
    def __init__(self, path: Path):
        super().__init__()
        self.current_directory = path
        self.data_manager = DataManager(path)
        self.command_pipeline_handler = CommandPipelineHandler()

        self.state = "file"
        self.loading = True

    def compose(self) -> ComposeResult:
        # yield Header()
        yield Footer()

        # with Grid():
        with FlexSplitHorizontal(sizes=["20", "80", "0"], id="split_panel_main"):
            with FlexSplitVertical(sizes=["80", "20"], id="split_vertical"):
                with ScrollableContainer(id="left_panel"):
                    self.toggle_tree = ToggleTree(label=f"{ENABLED_FOLDER} {self.current_directory.name}", id="tree_display", data_manager=self.data_manager, directory_path=self.current_directory)
                    yield self.toggle_tree
                with ScrollableContainer(id="info_display_panel"):
                    self.info_display = InfoDisplay(id="info_display", expand=True)
                    yield self.info_display
            with Vertical(id="right_panel"):
                with Vertical(id="tab_and_table"):
                    with Vertical(id="tab_and_buttons"):
                        with TabbedContent(id="tab_panel"):
                            with TabPane("Files", id="tab_files"):
                                with Horizontal(id="buttons_files_row"):
                                    yield Button(label="Enable All", id="enable_files_button", classes="file_buttons")
                                    yield Button(label="Disable All", id="disable_files_button", classes="file_buttons")
                                    yield Button(label="Populate All", id="populate_files_button", classes="file_buttons")
                                    yield Button(label="Refresh", id="refresh_files_button", classes="file_buttons")
                                self.file_table = FileTable(id="file_table")
                                yield self.file_table
                            with TabPane("Folders", id="tab_folders"):
                                with Horizontal(id="buttons_folders_row"):
                                    yield Button(label="Enable All", id="enable_folders_button", classes="folder_buttons")
                                    yield Button(label="Disable All", id="disable_folders_button", classes="folder_buttons")
                                    yield Button(label="Populate All", id="populate_folders_button", classes="folder_buttons")
                                    yield Button(label="Refresh", id="refresh_folders_button", classes="folder_buttons")
                                self.folder_table = FolderTable(id="folder_table")
                                yield self.folder_table
                            with TabPane("Help", id="tab_help"):
                                yield MarkdownViewer(generate_readme_markdown(), show_table_of_contents=False, id="help_markdown2")

            
                with Vertical(id="right_sub_panel"):
                    self.output_display = OutputDisplay(id="output_display", expand=True)
                    yield self.output_display
                    self.input_field = Input(id="input_command")
                    self.input_field.suggester = CommandSuggester()
                    yield self.input_field
            # yield Static("Hello static one")
            yield MarkdownViewer(generate_readme_markdown(), show_table_of_contents=True, id="help_markdown")
            # yield Static("Hello static one")
            # yield Static("Hello static one")


    def on_mount(self) -> None:
        tree = self.query_one("#tree_display", ToggleTree)
        tree.guide_depth = 2
        self.file_table = self.query_one("#file_table", FileTable)
        self.folder_table = self.query_one("#folder_table", FolderTable)
        self.query_one("#info_display_panel", ScrollableContainer).border_title = "Info"
        self.query_one("#right_sub_panel", Vertical).border_title = "Input"
        self.query_one("#tab_and_table", Vertical).border_title = "Table"
        self.data_manager.populate_tree(tree.root, self.current_directory, recursive=False)
        self.file_table.populate_table(self.data_manager.data["folders"])
        self.folder_table.populate_table(self.data_manager.data["folders"])
        self.input_field.focus()

        self.output_display.update_display("Hello There")
        signal_connector = SignalConnector(
            data_manager=self.data_manager, 
            file_table=self.file_table,
            folder_table=self.folder_table,
            info_display=self.info_display,
            output_display=self.output_display,
            toggle_tree=self.toggle_tree,
            command_pipeline_handler=self.command_pipeline_handler
        )
        signal_connector.connect_signals()
        self.loading = False

    def action_test(self) -> None:
        print("Starting action test...")
        self.data_manager.set_file_name("test", "2", "pop")

    def action_undo(self) -> None:
        print("Lets undo")
        self.loading = True
        self.data_manager.undo()

    def action_redo(self) -> None:
        self.data_manager.redo()

    def action_focus_tree(self) -> None:
        """Focus on the tree view panel."""
        self.toggle_tree.focus()

    def action_focus_data_table(self) -> None:
        """Focus on the data table panel."""
        self.file_table.focus()
    
    def action_focus_folder_table(self) -> None:
        """Focus on the data table panel."""
        self.folder_table.focus()

    def action_focus_input(self) -> None:
        """Focus on the input field panel."""
        self.input_field.focus()

    @on(Button.Pressed, "#enable_files_button")
    def enable_files(self) -> None:
        self.data_manager.enable_all_files(True)

    @on(Button.Pressed, "#disable_files_button")
    def disable_files(self) -> None:
        self.data_manager.enable_all_files(False)

    @on(Button.Pressed, "#enable_folders_button")
    def enable_folders(self) -> None:
        self.data_manager.enable_all_folders(True)

    @on(Button.Pressed, "#disable_folders_button")
    def disable_folders(self) -> None:
        self.data_manager.enable_all_folders(False)

    @on(Button.Pressed, "#refresh_folders_button")
    def refresh_folders(self) -> None:
        self.folder_table.populate_table(self.data_manager.data["folders"])
    
    @on(Button.Pressed, "#refresh_files_button")
    def refresh_files(self) -> None:
        self.file_table.populate_table(self.data_manager.data["folders"])

    @on(Button.Pressed, "#populate_folders_button")
    def populate_folders(self) -> None:
        self.toggle_tree._populate_folders_recursive()
        self.folder_table.populate_table(self.data_manager.data["folders"])
    
    @on(Button.Pressed, "#populate_files_button")
    def populate_files(self) -> None:
        self.toggle_tree.action_enable_all()
        # self.folder_table.populate_table(self.data_manager.data["folders"])

    @on(EditCellRequested)
    def handle_edit_cell_requested(self, event: EditCellRequested):
        def get_cell_value(row, column_index):
            """Helper function to safely extract text values from table cells."""
            value = event.sender.get_cell_at((row, column_index))
            return value.plain if isinstance(value, Text) else value

        def on_complete(new_value: str):
            new_value_plain = new_value.plain if isinstance(new_value, Text) else new_value

            if event.table_type == "file":
                file_id_col = FileTableColumns.get_column_index(FileTableColumns.ID.value["key"])
                folder_id_col = FileTableColumns.get_column_index(FileTableColumns.PID.value["key"])
            else:  # "folder"
                folder_id_col = FolderTableColumns.get_column_index(FolderTableColumns.ID.value["key"])

            folder_id = get_cell_value(event.row, folder_id_col)
            old_name = get_cell_value(event.row, FileTableColumns.get_column_index(FileTableColumns.CURRENT_NAME.value["key"]))

            if event.table_type == "file":
                file_id = get_cell_value(event.row, file_id_col)
                print(f"file_id: {file_id}, folder_id: {folder_id}, new_value: {new_value_plain}")
                self.data_manager.set_file_name(folder_id, file_id, new_value_plain)
            else:
                self.data_manager.set_folder_name(folder_id, new_value_plain)

        self.push_screen(EditCellScreen(event.value, on_complete))

    @on(Input.Submitted, "#input_command")
    def handle_input_command(self, event: Input.Submitted):
        input_command = event.value
        success = self.command_pipeline_handler.process_input(input_command, self.state)
        self.input_field.clear()

    from textual.widgets import TabbedContent

    @on(TabbedContent.TabActivated)
    def handle_tab_change(self, event: TabbedContent.TabActivated) -> None:
        """Detects when a tab is switched and updates state."""
        # if event.pane.id
        if event.pane.id == "tab_files":
            self.state = "file"
            self.file_table.populate_table(self.data_manager.data["folders"])
            self.output_display.update_display("Switched to File State.")
        elif event.pane.id == "tab_folders":
            self.state = "folder"
            self.folder_table.populate_table(self.data_manager.data["folders"])
            self.output_display.update_display("Switched to Folder State.")


    def action_history_down(self):
        """Navigate to the previous command in history."""
        previous_command = self.command_pipeline_handler.get_previous_command()
        if previous_command is not None:
            self.input_field.value = previous_command

    def action_history_up(self):
        """Navigate to the next command in history."""
        next_command = self.command_pipeline_handler.get_next_command()
        if next_command is not None:
            self.input_field.value = next_command

    def action_toggle_state(self) -> None:
        """Toggle between folder and file states."""
        if self.state == "folder":
            self.state = "file"
            self.output_display.update_display("Switched to File State.")
            # self.data_table.update_table("files")
        else:
            self.state = "folder"
            self.output_display.update_display("Switched to Folder State.")
            # self.data_table.update_table("folders")


def main():
    try:
        if len(sys.argv) > 1:
            provided_path = Path(sys.argv[1]).resolve()
            if not provided_path.exists():
                print(f"Warning: Provided path '{provided_path}' does not exist. Falling back to current directory.")
                provided_path = Path.cwd()
        else:
            provided_path = Path.cwd()

        Namnbyte(path=provided_path).run()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()