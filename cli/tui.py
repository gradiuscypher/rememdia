# ruff: noqa: RUF012
# for integration with iterm2, send this text at the start -
# uv --directory /Users/gradius/git/rememdia run cli tui
# to run textual debug from git repo:
# uv run textual run --dev -c uv run tui.py

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen, Screen
from textual.widgets import Footer, Input, Log, Static


class FindLink(Screen):
    BINDINGS = [
        Binding(
            key="escape",
            action="switch_mode('find')",
            description="Close Find",
        ),
    ]

    def compose(self) -> ComposeResult:
        yield Static("This is the find link screen.")
        yield Footer()


class Find(ModalScreen):
    BINDINGS = [
        Binding(key="e", action="update_text()", description="Find a link"),
        Binding(
            key="escape",
            action="back",
            description="Exit Find",
        ),
    ]

    def action_update_text(self) -> None:
        window_text = self.query_one("#textlog", Log)
        window_text.write_line("This is new data.")

    def action_back(self) -> None:
        self.app.switch_mode("base")

    def compose(self) -> ComposeResult:
        yield Log(id="textlog").write_line("Hello find.")
        yield Footer()


class NoteInput(ModalScreen):
    BINDINGS = [
        Binding(
            key="escape",
            action="app.pop_screen",
        ),
    ]

    tags = []

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Static("Note:"),
                Input(id="notes"),
                id="note-input-container",
            ),
            Container(
                Static("Tags:", id="tag-status"),
                Input(id="tags"),
                id="tag-input-container",
            ),
            id="note-input",
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        note_value = self.query_one("#notes", Input).value

        if event.value and event.input.id == "tags":
            self.tags.append(event.value)

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8000/note",
                json={"note": note_value, "tags": self.tags},
            )

        note_str = f"{note_value}: [{self.tags}]"
        self.dismiss(note_str)
        self.tags.clear()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "tags" and event.value and event.value[-1] == " ":
            tag_list = self.query_one("#tag-status", Static)
            tag = event.value.strip()
            self.tags.append(tag)
            tag_list.update("Tags: " + " ".join(self.tags))
            event.input.clear()


class Save(ModalScreen):
    CSS_PATH = "tui.tcss"
    BINDINGS = [
        Binding(key="l", action="link", description="Save a link"),
        Binding(key="n", action="note", description="Save a note"),
        Binding(
            key="escape",
            action="back",
            description="Exit Save",
        ),
    ]

    def action_back(self) -> None:
        self.app.switch_mode("base")

    def action_link(self) -> None:
        window_text = self.query_one("#textlog", Log)
        window_text.write_line("This is data in the save screen")

    def action_note(self) -> None:
        def write_note(note_str: str | None) -> None:
            window_text = self.query_one("#textlog", Log)
            if note_str:
                window_text.write_line(note_str)

        self.app.push_screen(NoteInput(id="note-input"), write_note)

    def compose(self) -> ComposeResult:
        yield Log(id="textlog").write_line("Hello save.")
        yield Footer()


class Base(Screen):
    def compose(self) -> ComposeResult:
        yield Static("This is the base mode.")
        yield Footer()


class RemTui(App):
    BINDINGS = [
        Binding(key="s", action="switch_mode('save')", description="Save"),
        Binding(key="f", action="switch_mode('find')", description="Find"),
    ]

    MODES = {"base": Base, "save": Save, "find": Find}

    def compose(self) -> ComposeResult:
        yield Static(f"{self.current_mode}")
        yield Footer()

    def on_mount(self) -> None:
        self.switch_mode("base")


if __name__ == "__main__":
    app = RemTui()
    app.run()
