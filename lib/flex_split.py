from textual import events
from textual.app import App, ComposeResult
from textual import on
from textual.geometry import Offset, Size
from textual.widget import Widget
from textual.widgets import Rule, Static
from textual.containers import Horizontal, Vertical
from typing import Any, List
from textual import work
from enum import Enum
import re

class SplitSeparatorState(Enum):
    DEFAULT = "default"
    HOVERED = "hovered"
    ACTIVE = "active"

# TODO: Merge Separtors to one, merge FlexSplit to one
# TODO: Fix last panel fill space
class SplitSeparator(Rule):
    """A draggable separator for vertical splits."""
    
    def __init__(self, *args: Any, state_classes: dict = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.line_style = "blank"

        # Default state classes, can be overridden by user
        self.state_classes = state_classes or {
            SplitSeparatorState.DEFAULT: "separator-default",
            SplitSeparatorState.HOVERED: "separator-hover",
            SplitSeparatorState.ACTIVE: "separator-active",
        }

        # Internal state tracking
        self.state = SplitSeparatorState.DEFAULT
        self._grabbed = False
        self._hovered = False
        
        # Initialize with the default class
        self.add_class(self.state_classes[self.state])
        self.styles.margin = 0
        self._update_style()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse press to start dragging the separator."""
        self._grabbed = True
        self.state = SplitSeparatorState.ACTIVE
        self._update_style()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse release after dragging the separator."""
        self._grabbed = False
        if not self._hovered:
            self.state = SplitSeparatorState.DEFAULT
        self._update_style()

    def on_leave(self, event: events.Leave) -> None:
        """Handle mouse leaving the separator."""
        self._hovered = False
        if not self._grabbed:
            self.state = SplitSeparatorState.DEFAULT
        self._update_style()

    def on_enter(self, event: events.Enter) -> None:
        """Handle mouse entering the separator."""
        print(f"Container size is {self.container_size}")
        self._hovered = True
        if not self._grabbed:
            self.state = SplitSeparatorState.HOVERED
        self._update_style()

    def _update_style(self) -> None:
        """Update the separator's class based on the current state."""
        # Remove all state-related classes
        for state in SplitSeparatorState:
            self.remove_class(self.state_classes[state])

        # Add class for the current state
        self.add_class(self.state_classes[self.state])


class VerticalSplitSeparator(Rule):
    """A draggable separator for vertical splits."""
    
    def __init__(self, *args: Any, state_classes: dict = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.line_style = "blank"

        # Default state classes, can be overridden by user
        self.state_classes = state_classes or {
            SplitSeparatorState.DEFAULT: "separator-default",
            SplitSeparatorState.HOVERED: "separator-hover",
            SplitSeparatorState.ACTIVE: "separator-active",
        }

        # Internal state tracking
        self.state = SplitSeparatorState.DEFAULT
        self._grabbed = False
        self._hovered = False
        
        # Initialize with the default class
        self.add_class(self.state_classes[self.state])
        self.styles.margin = 0
        self._update_style()

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse press to start dragging the separator."""
        self._grabbed = True
        self.state = SplitSeparatorState.ACTIVE
        self._update_style()

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Handle mouse release after dragging the separator."""
        self._grabbed = False
        if not self._hovered:
            self.state = SplitSeparatorState.DEFAULT
        self._update_style()

    def on_leave(self, event: events.Leave) -> None:
        """Handle mouse leaving the separator."""
        self._hovered = False
        if not self._grabbed:
            self.state = SplitSeparatorState.DEFAULT
        self._update_style()

    def on_enter(self, event: events.Enter) -> None:
        """Handle mouse entering the separator."""
        print(f"Container size is {self.container_size}")
        print(f"self.parent.container_size {self.parent.container_size}")
        # self.parent.container_size
        self._hovered = True
        if not self._grabbed:
            self.state = SplitSeparatorState.HOVERED
        self._update_style()

    def _update_style(self) -> None:
        """Update the separator's class based on the current state."""
        # Remove all state-related classes
        for state in SplitSeparatorState:
            self.remove_class(self.state_classes[state])

        # Add class for the current state
        self.add_class(self.state_classes[self.state])


# TODO: Clean up code
class FlexSplitHorizontal(Horizontal):
    """A container for a flexible horizontal split with draggable separators."""
    def __init__(self, *children, name = None, id = None, classes = None, disabled = False, markup = True, sizes: list[float] = None):
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, markup=markup)
        self.widgets: List[Widget] = []
        self.my_children = list(children)
        self.separators: List[SplitSeparator] = []
        self.sizes = sizes

        self.widget_before_current_size = None
        self.widget_after_current_size = None
        self.separator_size = 2
        self.is_dragging: bool = False
        self.drag_start_offset: Offset = None
        self.widget_size_before_drag: Size = None
        self.index_of_dragged_separator: int = None

    def _on_mount(self, event):
        super()._on_mount(event)
        self.app.call_after_refresh(self._initialize_widths)

    def on_event(self, event):
        return super().on_event(event)

    def on_resize(self):
        self.call_after_refresh(self.scale_widgets)
        self.set_timer(1, self.scale_widgets)

    def compose_add_child(self, widget) -> None:
        if self.widgets:
            separator = SplitSeparator("vertical", classes="separator-horizontal")
            self.separators.append(separator)
            super().compose_add_child(separator)  # Add separator before new child
        self.widgets.append(widget)
        super().compose_add_child(widget)

    def update_separator_positions(self):
        """Update the positions of separators based on widget widths."""
        current_position = 0  # Start from the beginning of the container
        for i, widget in enumerate(self.widgets):
            if widget.outer_size.width > 0:  # Only update positions if the widget has width
                current_position += widget.outer_size.width
                if i < len(self.separators):
                    separator = self.separators[i]
                    separator.styles.left = current_position
                    current_position += self.separator_size

    def ensure_size(self):
        total_separator_size = self.separators[0].container_size.width * len(self.separators)
        container_size = self.container_size
        total_widget_width = sum(widget.outer_size.width for widget in self.widgets)
        available_size = container_size.width - total_separator_size
        
        if total_widget_width == 0 and container_size.width > total_separator_size:
            average = available_size / len(self.widgets)
            for widget in self.widgets:
                if average < 1:
                    average = 1
                widget.styles.width = f"{average}"
            # self._initialize_widths()

    def scale_widgets(self):
        """Scale widget widths based on actual widget sizes to fit within the available space."""
        total_separator_size = self.separators[0].container_size.width * len(self.separators)
        container_size = self.container_size
        available_size = container_size.width - total_separator_size

        # Calculate the total width of all widgets (using their actual sizes)
        total_widget_width = sum(widget.outer_size.width for widget in self.widgets)

        for widget in self.widgets:
            print(f"widget.outer_size is {widget.outer_size.width}")
            print(f"widget.size is {widget.size.width}")
            # if widget.outer_size.width == 0:
                
                # print("This widget is zero")

        print(f"Total separator size: {total_separator_size}")
        print(f"Container size: {container_size.width}")
        print(f"Available space for widgets: {available_size}")
        print(f"Total width of all widgets: {total_widget_width}")
        self.ensure_size()
        if total_widget_width == 0:
            print("Total widget width is zero, skipping scaling.")
            return  # Or you could set default heights or apply other behavior

        # Calculate the total width to scale
        scaled_widths = []
        total_scaled_width = 0

        # Scale widgets proportionally based on their actual size
        for widget in self.widgets:
            widget_width = (widget.outer_size.width / total_widget_width) * available_size
            scaled_widths.append(int(widget_width))
            total_scaled_width += scaled_widths[-1]
            print(f"Widget {widget} scaled width: {scaled_widths[-1]}")

        # If there is any leftover space, assign it to the last widget
        leftover_space = available_size - sum(scaled_widths)
        if leftover_space > 0:
            # Find a valid widget (not zero-width) to absorb the leftover space
            for i in reversed(range(len(scaled_widths))):
                if scaled_widths[i] > 0:  # Assign to the last *non-zero* width widget
                    print(f"Adding leftover space ({leftover_space}) to widget {i}.")
                    scaled_widths[i] += leftover_space
                    break

        # Apply the scaled widths to the widgets
        for i, widget in enumerate(self.widgets):
            widget.styles.width = scaled_widths[i]
            print(f"Applied width to widget {i} ({widget}): {scaled_widths[i]}")

        print(f"Container size: {container_size.width}")
        print(f"Total separator size: {total_separator_size}")
        print(f"scaled_widths size: {sum(scaled_widths)}")

        # self.ensure_size()
        # self.update_separator_positions()


    def _initialize_widths(self) -> None:
        """Initialize widths for widgets, using custom sizes if provided."""
        if not self.widgets:
            return

        total_separator_size = self.separators[0].container_size.width * len(self.separators)
        container_size = self.container_size
        available_size = container_size.width - total_separator_size

        if self.sizes and len(self.sizes) == len(self.widgets):
            # Use provided sizes
            for widget, size in zip(self.widgets, self.sizes):
                widget_width = (float(size) / 100) * available_size
                # Ensure widget width is at least 1px
                if widget_width < 1:
                    widget_width = 1
                widget.styles.width = f"{widget_width}"
        else:
            average = available_size / len(self.widgets)
            for widget in self.widgets:
                # Ensure widget width is at least 1
                if average < 1:
                    average = 1
                widget.styles.width = f"{average}"

    def get_first_separator_under_mouse(self):
        """Fetch the first separator under the mouse."""
        for separator in self.separators:
            if separator.is_mouse_over:
                return separator
        return None


    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse press to start dragging the separator."""
        total_separator_size = self.separators[0].container_size.width * len(self.separators)
        container_size = self.container_size



        available_size = container_size.width - total_separator_size
        # widget, _ = self.screen.get_widget_at(event.screen_x, event.screen_y)
        separator = self.get_first_separator_under_mouse()
        if separator:
            print("We are over separator")
            self.index_of_dragged_separator = self.separators.index(separator)
            self.widget_size_before_drag = self.widgets[self.index_of_dragged_separator].outer_size
            self.widget_before = self.widgets[self.index_of_dragged_separator]
            self.widget_before_current_size = self.widgets[self.index_of_dragged_separator].outer_size
            # self.content_size
            # self.size
            self.size
            self.widget_after = self.widgets[self.index_of_dragged_separator + 1]
            self.widget_after_current_size = self.widgets[self.index_of_dragged_separator + 1].outer_size
            self.is_dragging = True
            self.drag_start_offset = event.screen_offset
            separator.state = SplitSeparatorState.ACTIVE
            separator._update_style()

    def calculate_total_separator_width(self, widget: Widget, split_direction: str) -> int:
        """Recursively calculate the total width of separators within a widget, considering its direction."""
        total_separator_width = 0

        # If the widget is an instance of a FlexSplit (either horizontal or vertical), check its separators
        if isinstance(widget, FlexSplitHorizontal) or isinstance(widget, FlexSplitVertical):
            # Check if the widget's split direction matches the provided direction
            if isinstance(widget, FlexSplitHorizontal) and split_direction == "horizontal":
                # Only add horizontal separators for horizontal splits
                total_separator_width += len(widget.separators) * self.separator_size
            elif isinstance(widget, FlexSplitVertical) and split_direction == "vertical":
                # Only add vertical separators for vertical splits
                total_separator_width += len(widget.separators) * self.separator_size

        # If the widget has children (nested splits), calculate their separator width recursively
        if hasattr(widget, 'widgets') and widget.widgets:
            for child_widget in widget.widgets:
                # Recursively calculate total separator width for child widgets, considering split direction
                total_separator_width += self.calculate_total_separator_width(child_widget, split_direction)

        return total_separator_width


    def calculate_total_width(self, widget: Widget) -> int:
        """Recursively calculate the total width of a widget, including nested splits."""
        total_width = widget.outer_size.width  # Start with the widget's own width

        # If the widget has children (i.e., nested splits), calculate their total width
        if hasattr(widget, 'widgets') and widget.widgets:
            for child_widget in widget.widgets:
                total_width += self.calculate_total_width(child_widget)  # Recursively calculate width of children

        return total_width

    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Update the width of the left part of the split while dragging."""
        if not self.is_dragging or self.index_of_dragged_separator is None:
            return

        dragged_offset = event.screen_offset - self.drag_start_offset

        widget_before_width = int(self.widget_before_current_size.width)
        widget_after_width = int(self.widget_after_current_size.width)

        container_width = self.container_size.width
        total_separator_size = self.calculate_total_separator_width(self, "horizontal")  # Total size of all separators
        available_space = container_width - total_separator_size
        available_range = widget_before_width + widget_after_width
        print(f"widget_before_width{widget_before_width}")
        print(f"widget_after_width{widget_after_width}")
        print(f"available_range{available_range}")

        new_widget_before_width = widget_before_width + dragged_offset.x
        new_widget_after_width = widget_after_width - dragged_offset.x

        if widget_before_width == 0 and new_widget_before_width < available_space:
            new_widget_before_width = max(0, new_widget_before_width)
            
        if widget_after_width == 0 and new_widget_after_width < available_space:
            new_widget_after_width = max(0, new_widget_after_width)

        widget_before_min_width = self.calculate_total_separator_width(self.widget_before, "horizontal")
        widget_after_min_width = self.calculate_total_separator_width(self.widget_after, "horizontal")

        if new_widget_before_width < widget_before_min_width or new_widget_after_width < widget_after_min_width:
            return  # Prevent shrinking below minimum width required for separators

        # if new_widget_before_width + new_widget_after_width > available_range:
        #     return  # Prevent going beyond the total available space

        if new_widget_before_width < 0 or new_widget_after_width < 0:
            return  # Prevent shrinking below 0

        if new_widget_before_width + new_widget_after_width > available_range:
            return  # Prevent going beyond the total available space
                
        self.widget_before.styles.width = f"{new_widget_before_width}"
        self.widget_after.styles.width = f"{new_widget_after_width}"

        for widget_before_child in self.widget_before.children:
            if isinstance(widget_before_child, FlexSplitHorizontal) or isinstance(widget_before_child, FlexSplitVertical):
                widget_before_child.scale_widgets()
        for widget_after_child in self.widget_after.children:
            if isinstance(widget_after_child, FlexSplitHorizontal) or isinstance(widget_after_child, FlexSplitVertical):
                widget_after_child.scale_widgets()


        # self.scale_widgets()



    def on_mouse_up(self) -> None:
        """Reset the dragging state after the mouse release."""
        self.is_dragging = False
        self.drag_start_offset = None
        self.widget_size_before_drag = None
        if self.index_of_dragged_separator is not None:
            dragged_separator = self.separators[self.index_of_dragged_separator]
            dragged_separator.state = SplitSeparatorState.DEFAULT
            dragged_separator._update_style()
        self.index_of_dragged_separator = None

class FlexSplitVertical(Vertical):
    """A container for a flexible horizontal split with draggable separators."""

    def __init__(self, *children, name = None, id = None, classes = None, disabled = False, markup = True, sizes: list[float] = None):
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled, markup=markup)
        self.widgets: List[Widget] = []
        self.my_children = list(children)
        self.separators: List[VerticalSplitSeparator] = []
        self.sizes = sizes

        self.widget_before_current_size = None
        self.widget_after_current_size = None
        self.separator_size = 2
        self.is_dragging: bool = False
        self.drag_start_offset: Offset = None
        self.widget_size_before_drag: Size = None
        self.index_of_dragged_separator: int = None


    def _on_mount(self, event):
        super()._on_mount(event)
        self.app.call_after_refresh(self._initialize_heights)

    def on_resize(self):
        self.call_after_refresh(self.scale_widgets)
        self.set_timer(1, self.scale_widgets)

    def compose_add_child(self, widget) -> None:
        if self.widgets:
            separator = VerticalSplitSeparator("horizontal", classes="separator-vertical")
            self.separators.append(separator)
            super().compose_add_child(separator)  # Add separator before new child
        self.widgets.append(widget)
        super().compose_add_child(widget)

    def scale_widgets(self):
        print("Scaling widgets")
        """Scale widget widths based on actual widget sizes to fit within the available space."""
        total_separator_size = self.separators[0].container_size.height * len(self.separators)
        container_size = self.container_size
        available_size = container_size.height - total_separator_size

        # Calculate the total height of all widgets (using their actual sizes)
        total_widget_height = sum(widget.outer_size.height for widget in self.widgets)

        print(f"Total separator size: {total_separator_size}")
        print(f"Container size: {container_size.height}")
        print(f"Available space for widgets: {available_size}")
        print(f"Total height of all widgets: {total_widget_height}")

        if total_widget_height == 0:
            print("Total widget height is zero, skipping scaling.")
            return  # Or you could set default heights or apply other behavior

        # Calculate the total height to scale
        scaled_heights = []
        total_scaled_height = 0

        # Scale widgets proportionally based on their actual size
        for widget in self.widgets:
            widget_height = (widget.outer_size.height / total_widget_height) * available_size
            scaled_heights.append(int(widget_height))
            total_scaled_height += scaled_heights[-1]
            print(f"Widget {widget} scaled height: {scaled_heights[-1]}")

        # If there is any leftover space, assign it to the last widget
        leftover_space = available_size - total_scaled_height
        if leftover_space > 0:
            print(f"Leftover space: {leftover_space}")
            scaled_heights[-1] += leftover_space
            print(f"Added leftover space to last widget, new height: {scaled_heights[-1]}")

        # Apply the scaled heights to the widgets
        for i, widget in enumerate(self.widgets):
            widget.styles.height = scaled_heights[i]
            print(f"Applied height to widget {i} ({widget}): {scaled_heights[i]}")

        print(f"Container size: {container_size.height}")
        print(f"Total separator size: {total_separator_size}")
        print(f"scaled_heights size: {sum(scaled_heights)}")



    def _initialize_heights(self) -> None:
        """Initialize heights for widgets, using custom sizes if provided."""
        if not self.widgets:
            return
        
        total_separator_size = self.separators[0].container_size.height * len(self.separators)
        container_size = self.container_size
        available_size = container_size.height - total_separator_size

        if self.sizes and len(self.sizes) == len(self.widgets):
            # Use provided sizes
            for widget, size in zip(self.widgets, self.sizes):
                # widget.styles.height = f"{size}%"
                widget_height = (float(size)/100) * available_size
                widget.styles.height = f"{widget_height}"
        else:
            average = available_size / len(self.widgets)
            for widget in self.widgets:
                widget.styles.height = f"{average}"


    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Handle mouse press to start dragging the separator."""
        total_separator_size = self.separators[0].container_size.height * len(self.separators)
        container_size = self.container_size
        available_size = container_size.height - total_separator_size
        # widget, _ = self.screen.get_widget_at(event.screen_x, event.screen_y)
        separator = self.get_first_separator_under_mouse()
        if separator:
            print("We are over separator")
            self.index_of_dragged_separator = self.separators.index(separator)
            self.widget_size_before_drag = self.widgets[self.index_of_dragged_separator].outer_size
            self.widget_before = self.widgets[self.index_of_dragged_separator]
            self.widget_before_current_size = self.widgets[self.index_of_dragged_separator].outer_size

            self.widget_after = self.widgets[self.index_of_dragged_separator + 1]
            self.widget_after_current_size = self.widgets[self.index_of_dragged_separator + 1].outer_size
            self.is_dragging = True
            self.drag_start_offset = event.screen_offset
            separator.state = SplitSeparatorState.ACTIVE
            separator._update_style()

    def get_first_separator_under_mouse(self):
        """Fetch the first separator under the mouse."""
        for separator in self.separators:
            if separator.is_mouse_over:
                return separator
        return None


    def on_mouse_move(self, event: events.MouseMove) -> None:
        """Update the height of the left part of the split while dragging."""
        if not self.is_dragging or self.index_of_dragged_separator is None:
            return
        

        dragged_offset = event.screen_offset - self.drag_start_offset
        print(f"Dragged offset: {dragged_offset.y}")

        widget_before_height = int(self.widget_before_current_size.height)
        widget_after_height = int(self.widget_after_current_size.height)
        available_range = widget_before_height + widget_after_height

        new_widget_before_height = widget_before_height + dragged_offset.y
        new_widget_after_height = widget_after_height - dragged_offset.y


        print(f"New widget before height: {new_widget_before_height}")
        print(f"New widget after height: {new_widget_after_height}")

        if new_widget_before_height < 0 or new_widget_after_height < 0:
            return

        if new_widget_before_height + new_widget_after_height > available_range:
            return
        
        if new_widget_before_height + new_widget_after_height != available_range:
            difference = available_range - (new_widget_before_height + new_widget_after_height)
            
            # If the difference is small, add it to the last widget
            if abs(difference) > 1:
                new_widget_after_height += difference
                
        self.widget_before.styles.height = f"{new_widget_before_height}"
        self.widget_after.styles.height = f"{new_widget_after_height}"

    def on_mouse_up(self) -> None:
        """Reset the dragging state after the mouse release."""
        self.is_dragging = False
        self.drag_start_offset = None
        self.widget_size_before_drag = None
        if self.index_of_dragged_separator is not None:
            dragged_separator = self.separators[self.index_of_dragged_separator]
            dragged_separator.state = SplitSeparatorState.DEFAULT
            dragged_separator._update_style()
        self.index_of_dragged_separator = None