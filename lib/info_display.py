from textual.widgets import Static, Label
from rich.text import Text
from .signal import Signal

class InfoDisplay(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount_of_folders = 0
        self.amount_of_enabled_folders = 0
        self.amount_of_files = 0
        self.amount_of_enabled_files = 0
        self.undo_count = 0
        self.redo_count = 0
        self.pending_changes = 0
        self.pending_folder_changes = 0
        self.refresh_display_signal = Signal()
        self.refresh_display_signal.connect(self.on_refresh_display)
        self.expand = True
        self.shrink = False
        self.update_display()

    def update_display(self):
        """Update the content of the InfoDisplay."""
        print(f"InfoDisplay height: {self.size.height}")
        # Define labels in a dictionary for easier management
        labels = {
            "folders": "Folders:",
            "files": "Files:",
            "undo": "Undo:",
        }

        # Determine the maximum width for all categories based on labels
        label_width = max(len(label) for label in labels.values())

        # Define the width for the numbers (e.g., you want the numbers to be aligned in a column)
        max_width = max(
            len(str(self.amount_of_folders)),
            len(str(self.amount_of_enabled_folders)),
            len(str(self.amount_of_files)),
            len(str(self.amount_of_enabled_files)),
            len(str(self.pending_changes)),
            len(str(self.pending_folder_changes)),
            len(str(self.undo_count)),
            len(str(self.redo_count)),
        )
        pending_max_width = max(
            len(str(self.pending_changes)),
            len(str(self.pending_folder_changes))
        )
        
        undo_padding = " " * (pending_max_width + 0)

        # Update the display with aligned labels and numbers
        self.update(
            f"[bold #5E81AC]{labels['folders']:<{label_width}}[/bold #5E81AC] "
            f"{self.amount_of_enabled_folders:>{max_width}}:[bold #EBCB8B]{self.pending_folder_changes:>{pending_max_width}}[/bold #EBCB8B] / {self.amount_of_folders}\n"
            f"[bold #5E81AC]{labels['files']:<{label_width}}[/bold #5E81AC] "
            f"{self.amount_of_enabled_files:>{max_width}}:[bold #EBCB8B]{self.pending_changes:>{pending_max_width}}[/bold #EBCB8B] / {self.amount_of_files}\n"
            f"[bold #BF616A]{labels['undo']:<{label_width}}[/bold #BF616A] "
            f"{' ' * max_width} {self.undo_count:>{pending_max_width}} / {self.redo_count}\n"
        )

    def on_refresh_display(self, display_data):
        """Force a re-update of the info display with new data."""
        self.amount_of_folders = display_data["amount_of_folders"]
        self.amount_of_enabled_folders = display_data["amount_of_enabled_folders"]
        self.amount_of_files = display_data["amount_of_files"]
        self.amount_of_enabled_files = display_data["amount_of_enabled_files"]
        self.undo_count = len(display_data["undo_stack"])
        self.redo_count = len(display_data["redo_stack"])
        self.pending_changes = display_data["pending_changes_count"]
        self.pending_folder_changes = display_data["pending_folder_changes_count"]

        self.update_display()


    def refresh_display(self, amount_of_folders, amount_of_enabled_folders, amount_of_files, amount_of_enabled_files, undo_stack, redo_stack, pending_changes_count):
        """Force a re-update of the info display with new data."""
        self.amount_of_folders = amount_of_folders
        self.amount_of_enabled_folders = amount_of_enabled_folders
        self.amount_of_files = amount_of_files
        self.amount_of_enabled_files = amount_of_enabled_files

        self.undo_count = len(undo_stack)
        self.redo_count = len(redo_stack)
        self.pending_changes = pending_changes_count
        # self.pending_changes = pending_changes_count

        self.update_display()


class OutputDisplay(Static):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_label = Label("", id="output_label")  # Add a text label inside OutputDisplay
        self.information_signal = Signal()
        self.information_signal.connect(self.on_information_signal)
        

    def _on_mount(self, event):
        self.mount(self.message_label)  # Attach it to the widget
        # return super()._on_mount(event)

    def update_display(self, message: str, feedback_type: str = "info"):
        self.styles.reset()
        self.message_label.styles.reset()
        self.message_label.styles.animate("opacity", 100, duration=0)

        colors = {
            "info": "#EBCB8B",
            "success": "#A3BE8C",
            "warning": "#D08770",
            "error": "#BF616A",
        }

        icons = {
            "info": "i",
            "success": "+",
            "warning": "!",
            "error": "x",
        }

        color = colors.get(feedback_type, "#ffffff")
        icon = icons.get(feedback_type, "i")

        formatted_message = f"[bold {color}]{icon} {message}[/bold {color}]"

        # Update only the text label, not the whole widget
        self.message_label.update(formatted_message)

        # Now animate only the text fading out
        self.message_label.styles.animate("opacity", 0, duration=3, on_complete=self.clear_display)

    def clear_display(self):
        """Clear only the text label, keeping the widget structure."""
        self.message_label.update("")
        # self.message_label.styles.opacity = 100  # Reset o

    def on_information_signal(self, data):
        message = data["message"]
        feedback_type = data["type"]
        context = data["context"]
        if context == "folder_enable":
            self.update_display(message, feedback_type)
        if context == "file_enable":
            self.update_display(message, feedback_type)
        elif context == "error":
            self.update_display(message, feedback_type)
        elif context == "file_rename":
            self.update_display(message, feedback_type)
        else:
            self.update_display(message, feedback_type)