from textual.screen import ModalScreen
from textual.widgets import Pretty
from textual.containers import Container
from textual import events

class GlobalVarsModal(ModalScreen[str]):
    w_global_vars = None

    def __init__(self, arsenalng_global_vars, name=None, id=None, classes=None):
        self.w_global_vars = Pretty(arsenalng_global_vars)
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        with Container():
            yield self.w_global_vars

    def on_click(self, event: events.Click) -> None:
        """Prevent selection of the DataTable"""
        event.prevent_default()
        event.stop()
        return

    def on_mouse_down(self, event: events.MouseDown) -> None:
        """Prevent selection of the DataTable"""
        event.prevent_default()
        event.stop()
        return

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ["enter", "escape"]:
            self.dismiss()

