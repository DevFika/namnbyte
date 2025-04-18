from textual.widgets import Tree
from pathlib import Path
from textual.binding import Binding
from .signal import Signal, InformationSignal
from lib import DataManager

# TODO: Decouple from DataManager
# 📂
# ✅☑️🔳🔳☐
ENABLED_FOLDER = f"[#A3BE8C]✓[/#A3BE8C]"
DISABLED_FOLDER = f"[#BF616A]✗[/#BF616A]"

class ToggleTree(Tree[bool]):
    BINDINGS = [
    Binding("a", "toggle_expand_all", "Expand all", show=True,),
    Binding("c", "toggle_collapse_all", "Collapse all", show=True,),
    Binding("x", "disable_all", "Disable all", show=True,),
    Binding("e", "enable_all", "Enable all", show=True),
    Binding("f", "toggle_folder", "Toggle folder", show=True),

    Binding("ctrl+right", "expand_selected_recursive", "Expand selected + children", show=True),
    Binding("ctrl+left", "collapse_selected_recursive", "Collapse selected + children", show=True),
    Binding("ctrl+down", "disable_selected_recursive", "Disable selected + children", show=True),
    Binding("ctrl+up", "enable_selected_recursive", "Enable selected + children", show=True),
    Binding("ctrl+t", "isolate_folder", "Isolate Folder", show=True),
    Binding("right", "expand_selected", "Expand selected", show=True),
    Binding("left", "collapse_selected", "Collapse selected", show=True),
    ]

    def __init__(self, data_manager: DataManager, directory_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = data_manager
        self.directory_path = directory_path
        self.information_signal = InformationSignal()
        self.toggle_signal = Signal()
        self.refresh_nodes_signal = Signal()
        self.refresh_nodes_signal.connect(self.on_refresh_nodes)


    def on_mount(self):
        super().on_mount()
        self.root.is_enabled = True
        self.root.path = self.directory_path
        self.border_title = "Tree"
        self.root.data = {}
        self.root.expand()

    def on_tree_node_expanded(self, event: Tree.NodeExpanded):
        node_data = event.node.data
        folder_id = node_data.get("folder_id", None)
        if folder_id is None:
            return
        self.data_manager.populate_subfolders(node = event.node, folder_id = folder_id)
        self.end_batch_update()

    def toggle_node_state(self, node):
        node.is_enabled = not node.is_enabled
        self.update_node_label(node)
        
        self.data_manager.update_folder_data(node)

    def isolate_node(self, selected_node):
        """Disable all nodes except the selected one"""
        self.data_manager.start_batch_update()
        def disable_all_except(node, keep_enabled):
            node.is_enabled = (node is keep_enabled)  # Only keep selected node enabled
            self.update_node_label(node)
            self.data_manager.update_folder_data(node)
            for child in node.children:
                disable_all_except(child, keep_enabled)

        # Disable all nodes except the selected one
        disable_all_except(self.root, selected_node)
        self.data_manager.end_batch_update()

    def update_node_state(self, node, enable: bool):
        """Helper to update the node state and recursively handle children."""
        node.is_enabled = enable
        self.update_node_label(node)  # Update label for current node
        self.data_manager.update_folder_data(node)

        # Recurse through all child nodes
        for child in node.children:
            self.update_node_state(child, enable)

    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        event.prevent_default()
        self.toggle_node_state(event.node)

    def update_node_label(self, node):
        icon = ENABLED_FOLDER if node.is_enabled else DISABLED_FOLDER
        color = "bold green" if node.is_enabled else "bold red"

        node.label = f"{icon} {node.label.plain.split(' ', 1)[1]}"
        node.styles = color

    def action_toggle_expand_all(self):
        self._populate_all_subfolders(self.root)
        self.root.expand_all()

    def action_toggle_collapse_all(self):
        self.root.collapse_all()

    def _set_node_state_recursive(self, node, enable: bool):
        # self.update_node_state(node, enable)
        node_data = node.data
        folder_id = node_data.get("folder_id", None)
        if folder_id is None:
            return
        if node.is_enabled != enable:  # Only update if the state is different
            node.is_enabled = enable
            self.data_manager.populate_subfolders(node = node, folder_id = folder_id)
            self.update_node_label(node)  # Update label for the current node
            self.data_manager.update_folder_data(node)
        
        # Recurse through all child nodes
        for child in node.children:
            self._set_node_state_recursive(child, enable)

    def action_disable_all(self):
        self.start_batch_update()
        self._set_node_state_recursive(self.root, enable=False)  # Disable all nodes
        self.end_batch_update()
    
    def action_enable_all(self):
        self.start_batch_update()
        self._set_node_state_recursive(self.root, enable=True)  # Enable all nodes
        self.end_batch_update()

    def action_expand_selected_recursive(self):
        node = self.cursor_node
        self._populate_all_subfolders(node)
        if node:
            node.expand_all()

    def action_collapse_selected_recursive(self):
        node = self.cursor_node
        if node:
            node.collapse_all()

    def action_isolate_folder(self):
        node = self.cursor_node
        self.isolate_node(node)

    def action_expand_selected(self):
        node = self.cursor_node
        node.expand()
    
    def action_collapse_selected(self):
        node = self.cursor_node
        node.collapse()

    def action_enable_selected_recursive(self):
        node = self.cursor_node
        if node:
            self.start_batch_update()
            self._set_node_state_recursive(node, True)
            self.end_batch_update()

    def action_disable_selected_recursive(self):
        node = self.cursor_node
        if node:
            self.start_batch_update()
            self._set_node_state_recursive(node, False)
            self.end_batch_update()

    def action_toggle_folder(self):
        node = self.cursor_node
        if node:
            self.toggle_node_state(node)

    def start_batch_update(self):
        """Start a batch update to suppress UI updates."""
        self.data_manager.start_batch_update()

    def end_batch_update(self):
        """End the batch update and trigger final UI refresh."""
        self.data_manager.end_batch_update()

    def refresh_nodes(self):
        """Refresh node labels based on the current state of data in the data_manager."""
        # First, sync the node states with the data from the DataManager
        self._sync_node_states_with_data(self.root)
        
        # Then, update the labels for all nodes
        self._refresh_node_labels(self.root)

    def _sync_node_states_with_data(self, node):
        """Sync node's enabled state with the data in the DataManager."""
        # Check the node's path in the DataManager and update its enabled state
        folder_id = node.data.get("folder_id", None)
        if folder_id in self.data_manager.data["folders"]:
            folder_data = self.data_manager.data["folders"][folder_id]
            node.is_enabled = folder_data.is_enabled
            self._update_node_label_with_name(node, folder_data.current_name)

        # Recursively sync all child nodes
        for child in node.children:
            self._sync_node_states_with_data(child)
        
    def _refresh_node_labels(self, node):
        """Recursively refresh node labels."""
        self.update_node_label(node)  # Update the label for the current node

        # Recursively do the same for child nodes
        for child in node.children:
            self._refresh_node_labels(child)

    def _update_node_label_with_name(self, node, name):
        """Update node label while preserving the correct icon."""
        icon = ENABLED_FOLDER if node.is_enabled else DISABLED_FOLDER
        node.label = f"{icon} {name}"

    def _populate_all_subfolders(self, node):
        """Recursively populate subfolders for all nodes."""
        folder_id = node.data.get("folder_id", None)
        if folder_id:
            self.data_manager.populate_subfolders(node=node, folder_id=folder_id)

        for child in node.children:
            self._populate_all_subfolders(child)

    def _populate_folders_recursive(self):
        self._populate_all_subfolders(self.root)

    def on_refresh_nodes(self, data=None):
        self.refresh_nodes()