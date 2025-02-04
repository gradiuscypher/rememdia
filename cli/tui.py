# ruff: noqa: RUF012
# for integration with iterm2, send this text at the start -
# uv --directory /Users/gradius/git/rememdia run cli tui
# to run textual debug from git repo:
# uv run textual run --dev -c uv run tui.py

import httpx
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import Footer, Input, Log, Static, Switch


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


class Find(Screen):
    BINDINGS = [
        Binding(key="l", action="find_links", description="Find a link"),
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

    def action_find_links(self) -> None:
        self.app.push_screen(FindLink(id="find-link"))

    def compose(self) -> ComposeResult:
        yield Log(id="textlog").write_line("Hello find.")
        yield Footer()


class NoteInput(Screen):
    BINDINGS = [
        Binding(
            key="escape",
            action="app.pop_screen",
        ),
        Binding(
            key="ctrl+r",
            action="reminder",
            key_display="ctrl+r",
            show=True,
            description="Reminder",
        ),
        Binding(
            key="ctrl+l",
            action="reading_list",
            key_display="ctrl+l",
            show=True,
            description="Reading List",
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
            Horizontal(
                Static("Reminder: ", classes="label"),
                Switch(value=False, id="reminder"),
                Static("Reading List: ", classes="label"),
                Switch(value=False, id="reading-list"),
            ),
            Footer(),
            id="note-input",
        )

    def action_reminder(self) -> None:
        reminder = self.query_one("#reminder", Switch)
        reminder.value = not reminder.value

    def action_reading_list(self) -> None:
        reading_list = self.query_one("#reading-list", Switch)
        reading_list.value = not reading_list.value

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        note_value = self.query_one("#notes", Input).value
        reminder_value = self.query_one("#reminder", Switch).value
        reading_value = self.query_one("#reading-list", Switch).value

        if event.value and event.input.id == "tags":
            self.tags.append(event.value)

        async with httpx.AsyncClient() as client:
            await client.post(
                "http://127.0.0.1:8000/note",
                json={
                    "note": note_value,
                    "tags": self.tags,
                    "reminder": reminder_value,
                    "reading": reading_value,
                },
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


class LinkInput(Screen):
    BINDINGS = [
        Binding(
            key="escape",
            action="app.pop_screen",
        ),
        Binding(
            key="ctrl+r",
            action="reminder",
            key_display="ctrl+r",
            show=True,
            description="Reminder",
        ),
        Binding(
            key="ctrl+l",
            action="reading_list",
            key_display="ctrl+l",
            show=True,
            description="Reading List",
        ),
    ]

    tags = []

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Static("Link:"),
                Input(id="links"),
                id="link-input-container",
            ),
            Container(
                Static("Summary:"),
                Input(id="summary"),
                id="summary-input-container",
            ),
            Container(
                Static("Tags:", id="tag-status"),
                Input(id="tags"),
                id="tag-input-container",
            ),
            Horizontal(
                Static("Reminder: ", classes="label"),
                Switch(value=False, id="reminder"),
                Static("Reading List: ", classes="label"),
                Switch(value=False, id="reading-list"),
            ),
            Footer(),
            id="link-input",
        )

    def action_reminder(self) -> None:
        reminder = self.query_one("#reminder", Switch)
        reminder.value = not reminder.value

    def action_reading_list(self) -> None:
        reading_list = self.query_one("#reading-list", Switch)
        reading_list.value = not reading_list.value

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        link_value = self.query_one("#links", Input).value
        summary_value = self.query_one("#summary", Input).value
        reminder_value = self.query_one("#reminder", Switch).value
        reading_value = self.query_one("#reading-list", Switch).value

        if event.value and event.input.id == "tags":
            self.tags.append(event.value)

        async with httpx.AsyncClient() as client:
            await client.post(
                "http://127.0.0.1:8000/link",
                json={
                    "url": link_value,
                    "summary": summary_value,
                    "tags": self.tags,
                    "reminder": reminder_value,
                    "reading": reading_value,
                },
            )

        link_str = f"{link_value}: [{self.tags}]"
        self.dismiss(link_str)
        self.tags.clear()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "tags" and event.value and event.value[-1] == " ":
            tag_list = self.query_one("#tag-status", Static)
            tag = event.value.strip()
            self.tags.append(tag)
            tag_list.update("Tags: " + " ".join(self.tags))
            event.input.clear()


class Save(Screen):
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
        def write_link(link_str: str | None) -> None:
            window_text = self.query_one("#textlog", Log)
            if link_str:
                window_text.write_line(link_str)

        self.app.push_screen(LinkInput(id="link-input"), write_link)

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
