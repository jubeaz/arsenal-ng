from textual.screen import ModalScreen
from textual.widgets import Pretty
from textual.containers import Container
from textual import events

class HelpModal(ModalScreen[str]):
    help = {
        "ESC": "Exit",
        "F1": "Help",
        "F2": "Manage global vars",
        "F3": "Reload global vars",
        "F4": "Save global vars",
        "F5": "Remove all global vars"
    }

    def compose(self):
        with Container():
            yield Pretty(self.help)

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

