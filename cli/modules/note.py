import httpx
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen, ModalScreen
from textual.widgets import DataTable, Footer, Input, Static, Switch


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

    def __init__(
        self,
        note_id: int | None = None,
        note: str = "",
        tags: list[str] = [],
        reminder: bool = False,
        reading: bool = False,
        is_editing: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tags = tags
        self.note_id = note_id
        self.note = note
        self.reminder = reminder
        self.reading = reading
        self.is_editing = is_editing

    def compose(self) -> ComposeResult:
        yield Container(
            Container(
                Static("Note:"),
                Input(id="notes", value=self.note),
                id="note-input-container",
            ),
            Container(
                Static("Tags: " + " ".join(self.tags), id="tag-status"),
                Input(id="tags"),
                id="tag-input-container",
            ),
            Horizontal(
                Static("Reminder: ", classes="label"),
                Switch(value=self.reminder, id="reminder"),
                Static("Reading List: ", classes="label"),
                Switch(value=self.reading, id="reading-list"),
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

        if not self.is_editing:
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
        else:
            if event.value and event.input.id == "tags":
                self.tags.append(event.value)

            async with httpx.AsyncClient() as client:
                await client.patch(
                    f"http://127.0.0.1:8000/note/{self.note_id}",
                    json={
                        "note": note_value,
                        "tags": self.tags,
                        "reminder": reminder_value,
                        "reading": reading_value,
                    },
                )
            self.dismiss()
            self.tags.clear()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "tags" and event.value and event.value[-1] == " ":
            tag_list = self.query_one("#tag-status", Static)
            tag = event.value.strip()
            self.tags.append(tag)
            tag_list.update("Tags: " + " ".join(self.tags))
            event.input.clear()


class FindNote(Screen):
    notes = []

    BINDINGS = [
        Binding(
            key="escape",
            action="app.pop_screen",
            description="Close Find",
        ),
        Binding(
            key="u",
            action="search",
            description="Search",
        ),
        Binding(
            key="c",
            action="clear_search",
            description="Clear Search",
        ),
        Binding(
            key="j",
            action="move_cursor('down')",
        ),
        Binding(
            key="k",
            action="move_cursor('up')",
        ),
        Binding(
            key="d",
            action="delete_row",
        ),
        Binding(
            key="e",
            action="edit_row",
        ),
    ]

    async def refresh_table(self) -> None:
        self.notes.clear()
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns(
            "ID",
            "Note",
            "Created At",
            "Tags",
            "Reminder",
            "Reading",
        )

        async with httpx.AsyncClient() as client:
            note_request = await client.get("http://localhost:8000/note")
            self.notes = note_request.json()
            for note in self.notes:
                table_id = note["note_id"]
                note_str = note["note"]
                created_at = note["created_at"]
                tags = note["tags"]
                reminder = "✅" if bool(note["reminder"]) else "❌"
                reading = "✅" if bool(note["reading"]) else "❌"
                table.add_row(
                    table_id,
                    note_str,
                    created_at,
                    tags,
                    reminder,
                    reading,
                )

    def update_table(self, search_string: str) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for note in self.notes:
            table_id = note["note_id"]
            note_str = note["note"]
            tags = note["tags"]
            created_at = note["created_at"]
            reminder = "✅" if bool(note["reminder"]) else "❌"
            reading = "✅" if bool(note["reading"]) else "❌"

            if any(search_string in s for s in [tags, note_str]) or search_string == "":
                table.add_row(
                    table_id,
                    note_str,
                    created_at,
                    tags,
                    reminder,
                    reading,
                )

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield Footer()

    async def on_mount(self) -> None:
        await self.refresh_table()

    def action_back(self) -> None:
        self.app.switch_mode("base")

    def action_search(self) -> None:
        def execute_search(search_str: str | None) -> None:
            if search_str:
                self.update_table(search_str)

        self.app.push_screen(FindNoteSearch(id="find-note-search"), execute_search)

    def action_clear_search(self) -> None:
        self.update_table("")

    def action_move_cursor(self, direction: str) -> None:
        table = self.query_one(DataTable)
        table.move_cursor(
            row=table.cursor_row + 1 if direction == "down" else table.cursor_row - 1
        )

    async def action_delete_row(self) -> None:
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        note_id = table.get_cell_at(table.cursor_coordinate)
        async with httpx.AsyncClient() as client:
            await client.delete(f"http://127.0.0.1:8000/note/{note_id}")
        table.remove_row(row_key)
        await self.refresh_table()

    async def action_edit_row(self) -> None:
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_data = table.get_row(row_key)

        self.app.push_screen(
            NoteInput(
                id="note-input",
                note_id=row_data[0],
                is_editing=True,
                note=row_data[1],
                tags=row_data[3],
            )
        )


class FindNoteSearch(ModalScreen):
    BINDINGS = [
        Binding(
            key="escape",
            action="app.pop_screen",
            description="Close Find",
        ),
    ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a note")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value:
            self.dismiss(event.value)
