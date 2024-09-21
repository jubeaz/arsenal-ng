from textual.widgets import ListView
from textual import events




class MouselessListView(ListView):
    selected = None

    def on_click(self, event: events.Click) -> None:
        """Prevent click"""
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

    def on_mouse_capture(self, event: events.MouseCapture) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        event.stop()
        return 
    def on_mouse_event(self, event: events.MouseEvent) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        event.stop()
        return 
    def on_mouse_release(self, event: events.MouseRelease) -> None:
        """Prevent DataTable scroll up"""
        event.prevent_default()
        event.stop()
        return 