# ruff: noqa: RUF012
# for integration with iterm2, send this text at the start -
# uv --directory /Users/gradius/git/rememdia run cli tui
# to run textual debug from git repo:
# uv run textual run --dev -c uv run tui.py

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Static

from modules.link import FindLink, LinkInput
from modules.note import FindNote, NoteInput, note_reminder_job, note_reading_job


class Find(Screen):
    CSS_PATH = "tui.tcss"
    BINDINGS = [
        Binding(key="l", action="find_links", description="Find a link"),
        Binding(key="n", action="find_notes", description="Find a note"),
        Binding(
            key="escape",
            action="back",
            description="Exit Find",
        ),
    ]

    def action_back(self) -> None:
        self.app.switch_mode("base")

    def action_find_links(self) -> None:
        self.app.push_screen(FindLink(id="find-link"))

    def action_find_notes(self) -> None:
        self.app.push_screen(FindNote(id="find-note"))

    def compose(self) -> ComposeResult:
        yield Footer()


class Save(Screen):
    CSS_PATH = "tui.tcss"
    BINDINGS = [
        Binding(key="l", action="link", description="Save a link"),
        Binding(key="n", action="note", description="Save a note"),
        Binding(
            key="escape",
            action="app.switch_mode('base')",
            description="Exit Save",
        ),
    ]

    def action_back(self) -> None:
        self.app.switch_mode("base")

    def action_link(self) -> None:
        self.app.push_screen(LinkInput(id="link-input"))

    def action_note(self) -> None:
        self.app.push_screen(NoteInput(id="note-input"))

    def compose(self) -> ComposeResult:
        yield Footer()


class Base(Screen):
    BINDINGS = [
        Binding(key="s", action="save", description="Save"),
        Binding(key="f", action="find", description="Find"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("This is the base mode.")
        yield Footer()

    def action_save(self) -> None:
        self.app.switch_mode("save")

    def action_find(self) -> None:
        self.app.switch_mode("find")


class RemTui(App):
    MODES = {"base": Base, "save": Save, "find": Find}

    def compose(self) -> ComposeResult:
        yield Static(f"{self.current_mode}")
        yield Footer()

    def on_mount(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(note_reminder_job, "interval", seconds=5)
        # self.scheduler.add_job(note_reading_job, "interval", seconds=10)
        self.scheduler.start()
        self.switch_mode("base")


if __name__ == "__main__":
    app = RemTui()
    app.run()
