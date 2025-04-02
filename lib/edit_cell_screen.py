from typing import Callable
from textual import on
from textual.events import Click
from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Input, Button
from textual.containers import Container
from textual.binding import Binding
from textual.events import Key

class EditCellScreen(ModalScreen):
    BINDINGS = [
        Binding("escape", "exit", "Focus on Tree View", show=True),
    ]
    def __init__(self, cell_value: str, on_complete: Callable[[str], None]):
        super().__init__()
        self.cell_value = cell_value
        self.on_complete = on_complete

    def compose(self) -> ComposeResult:
        yield Input(id="edit_cell_input")

    def on_mount(self) -> None:
        cell_input = self.query_one("#edit_cell_input", Input)
        cell_input.value = str(self.cell_value)
        cell_input.cursor_position = 0
        cell_input.select_on_focus = False
        cell_input.focus()

    def action_exit(self):
        if len(self.app._screen_stack) > 1:  # There must be more than just the main screen
            self.app.pop_screen()
        else:
            print("Warning: Tried to pop screen when only the main screen was present.")

    @on(Click)
    def click(self, event: Click) -> None:
        clicked, _ = self.get_widget_at(event.screen_x, event.screen_y)
        # Close the screen if the user clicks outside the modal content
        if clicked is self:
            self.app.pop_screen()

    @on(Input.Submitted)
    def rename_input_submitted(self, event: Input.Submitted):
        self.on_complete(event.value)
        self.app.pop_screen()