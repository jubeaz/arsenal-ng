from textual.screen import ModalScreen
from textual import events



class MouselessModal(ModalScreen[str]):
    focus_save = None

    def on_click(self, event: events.Click) -> None:
        """Prevent Click"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent MouseDown"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_up(self, event: events.MouseUp) -> None:
        """Prevent MouseUp"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_mouse_scroll_down(self, event: events.MouseScrollDown) -> None:
        """Prevent MouseScrollDown"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_scroll_up(self, event: events.MouseScrollUp) -> None:
        """Prevent MouseScrollUp"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_capture(self, event: events.MouseCapture) -> None:
        """Prevent MouseCapture"""
        event.prevent_default()
        event.stop()
        return 
    def on_mouse_event(self, event: events.MouseEvent) -> None:
        """Prevent MouseEvent"""
        event.prevent_default()
        event.stop()
        return 
    def on_mouse_release(self, event: events.MouseRelease) -> None:
        """Prevent MouseReleasep"""
        event.prevent_default()
        event.stop()
        return 
 