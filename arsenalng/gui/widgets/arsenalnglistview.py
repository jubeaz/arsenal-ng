from textual.widgets import ListView, ListItem, Label
from textual import events
from textual.app import ComposeResult


class LabelItem(ListItem):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label

    def compose( self ) -> ComposeResult:
        yield Label(self.label)

class ArsenalNGListView(ListView):
    selected = None
    def on_click(self, event: events.MouseDown) -> None:
        """Prevent selection of the DataTable"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent click"""
        event.prevent_default()
        event.stop()
        return
        
    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Prevent click"""
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
#    def on_list_view_selected(self, event: ListView.Selected):
#        self.selected = event.item.label
#        return
#    def on_key(self, event: events.Key) -> None:
#        event.stop()
#        if event.key in ["tab", "right"]:
#            self.press()
#        elif event.key == "up":
#            self.move_cursor_up()
#        elif event.key == "down":
#            self.move_cursor_down()