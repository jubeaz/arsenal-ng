from textual.widgets import ListItem, Label
from textual import events
from textual.app import ComposeResult


class MouselessLabelItem(ListItem):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label

    def compose( self ) -> ComposeResult:
        yield Label(self.label)

    def on_click(self, event: events.Click) -> None:
        """Prevent click"""
        event.prevent_default()
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent click"""
        event.prevent_default()
        return
        
    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Prevent click"""
        event.prevent_default()
        return

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Prevent DataTable scroll down"""
        event.prevent_default()
        return

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        return

    def on_mouse_capture(self, event: events.MouseCapture) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        return 
    def on_mouse_event(self, event: events.MouseEvent) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        return 
    def on_mouse_release(self, event: events.MouseRelease) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        return 
       