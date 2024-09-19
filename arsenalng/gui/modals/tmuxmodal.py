from textual.screen import ModalScreen
from textual.widgets import Input
from textual.containers import Container
from textual import events

class TmuxModal(ModalScreen[str]):
    arsenalng_global_vars = None
    w_session_name = None
    w_window_name = None
    w_pane_id = None
    focus_save = None

    def __init__(self, arsenalng_global_vars, name=None, id=None, classes=None):
        self.arsenalng_global_vars = arsenalng_global_vars
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        with Container():
            self.w_session_name = Input(id="arsenalng_tmux_session_name", placeholder="arsenalng_tmux_session_name", type="text", value=self.arsenalng_global_vars["arsenalng_tmux_session_name"])
            self.w_window_name = Input(id="arsenalng_tmux_window_name", placeholder="arsenalng_tmux_window_name", type="text", value=self.arsenalng_global_vars["arsenalng_tmux_window_name"])
            self.w_pane_id = Input(id="arsenalng_tmux_pane_id", placeholder="arsenalng_tmux_pane_id", type="text", value=self.arsenalng_global_vars["arsenalng_tmux_pane_id"])
            yield self.w_session_name
            yield self.w_window_name
            yield self.w_pane_id

    def on_mount(self) -> None:
        self.set_focus(self.w_session_name)
        self.focus_save = self.focused

    def on_click(self, event: events.Click) -> None:
        """Prevent click"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent click"""
        event.prevent_default()
        event.stop()
        self.set_focus(self.focus_save)
        return

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ["tab", "down", "shift+tab", "up"]:
            if event.key == "tab" or event.key == "down":
                self.focus_next()
            elif event.key == "shift+tab" or event.key == "up":
                self.focus_previous()
            self.focus_save = self.focused
        elif event.key == "left":
            self.focused.action_cursor_left()
        elif event.key == "right":
            self.focused.action_cursor_right()
        elif event.key == "backspace":
            self.focused.action_delete_left()
        elif event.key == "delete":
            self.focused.action_delete_right()
        elif event.key == "home":
            self.focused.action_home()
        elif event.key == "end":
            self.focused.action_end()
        elif event.key == "enter":
            if self.w_session_name.value != "" and self.w_window_name.value != "":
                result = {}
                result["arsenalng_tmux_session_name"] = self.w_session_name.value
                result["arsenalng_tmux_window_name"] = self.w_window_name.value
                result["arsenalng_tmux_pane_id"] = self.w_pane_id.value
                self.dismiss(result)
        elif event.key == "escape":
            self.dismiss()
