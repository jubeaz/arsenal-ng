from textual.widgets import Label
from textual import events

from arsenalng.models.command import Command
from arsenalng.gui.modals.mouselessmodal import MouselessModal

class CheatPreviewModal(MouselessModal):
    w_cheat_preview = None
    cmd = None

    def __init__(self, cheat, name=None, id=None, classes=None):  # noqa: A002
        self.w_cheat_preview = Label("", id="cheatpreviewmodal_cmd_preview")
        self.cmd = Command(cheat, {})
        super().__init__(name=name, id=id, classes=classes)

    def compose(self):
        yield self.w_cheat_preview
        self.w_cheat_preview.update(f"{self.cmd.description}\n-----\n{self.cmd.preview()}")    

    def on_mount(self) -> None:
        self.set_focus(self.w_cheat_preview)
        self.focus_save = self.focused

    def on_key(self, event: events.Key) -> None:
        event.stop()
        if event.key in ["enter", "escape"]:
            self.dismiss()

