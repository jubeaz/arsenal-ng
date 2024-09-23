from textual.widgets import Pretty
from textual.containers import Container
from textual import events

from arsenalng.gui.modals.mouselessmodal import MouselessModal

class GlobalVarsModal(MouselessModal):
    w_global_vars = None

    def __init__(self, arsenalng_global_vars, name=None, id=None, classes=None):  # noqa: A002
        self.w_global_vars = Pretty(arsenalng_global_vars)
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        with Container():
            yield self.w_global_vars

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ["enter", "escape"]:
            self.dismiss()

