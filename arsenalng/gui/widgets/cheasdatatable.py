from textual.widgets import DataTable
from textual import events

class CheatsDataTable(DataTable):
    def on_click(self, event: events.MouseDown) -> None:
        """Prevent selection of the DataTable"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Prevent DataTable scroll down"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        event.stop()
        return