from os import getenv

import httpx

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import Screen, ModalScreen
from textual.suggester import SuggestFromList
from textual.widgets import DataTable, Footer, Input, Static, Switch

API_HOST = getenv("API_HOST", "http://localhost:8000")


class FindLink(Screen):
    links = []

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
            description="Edit Row",
        ),
    ]

    async def refresh_table(self, result: bool | None = None) -> None:
        self.links.clear()
        table = self.query_one(DataTable)
        table.clear(columns=True)
        table.cursor_type = "row"
        table.add_columns(
            "ID",
            "URL",
            "Summary",
            "Tags",
            "Reminder",
            "Reading",
            "Meta.Title",
            "Meta.Description",
        )

        async with httpx.AsyncClient() as client:
            link_request = await client.get(f"{API_HOST}/link")
            self.links = link_request.json()
            for link in self.links:
                table_id = link["link_id"]
                url = link["url"]
                summary = link["summary"]
                tags = link["tags"]
                meta_title = link["meta_title"][:50]
                meta_description = link["meta_description"][:50]
                reminder = "✅" if bool(link["reminder"]) else "❌"
                reading = "✅" if bool(link["reading"]) else "❌"
                table.add_row(
                    table_id,
                    url,
                    summary,
                    tags,
                    reminder,
                    reading,
                    meta_title,
                    meta_description,
                )

    def update_table(self, search_string: str) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for link in self.links:
            table_id = link["link_id"]
            url = link["url"]
            summary = link["summary"]
            tags = link["tags"]
            meta_title = link["meta_title"][:50]
            meta_description = link["meta_description"][:50]
            reminder = "✅" if bool(link["reminder"]) else "❌"
            reading = "✅" if bool(link["reading"]) else "❌"

            if (
                any(
                    search_string in s
                    for s in [url, summary, tags, meta_title, meta_description]
                )
                or search_string == ""
            ):
                table.add_row(
                    table_id,
                    url,
                    summary,
                    tags,
                    reminder,
                    reading,
                    meta_title,
                    meta_description,
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

        self.app.push_screen(FindLinkSearch(id="find-link-search"), execute_search)

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
        link_id = table.get_cell_at(table.cursor_coordinate)
        async with httpx.AsyncClient() as client:
            await client.delete(f"{API_HOST}/link/{link_id}")
        table.remove_row(row_key)
        await self.refresh_table()

    async def action_edit_row(self) -> None:
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_data = table.get_row(row_key)

        await self.app.push_screen(
            LinkInput(
                link_id=row_data[0],
                link=row_data[1],
                summary=row_data[2],
                tags=row_data[3],
                reading=True if row_data[4] == "✅" else False,
                reminder=True if row_data[5] == "✅" else False,
                is_editing=True,
            ),
            self.refresh_table,
        )


class FindLinkSearch(ModalScreen):
    BINDINGS = [
        Binding(
            key="escape",
            action="app.pop_screen",
            description="Close Find",
        ),
    ]

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search for a link")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.value:
            self.dismiss(event.value)


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

    def __init__(
        self,
        link_id: int | None = None,
        link: str = "",
        summary: str = "",
        tags: list[str] = [],
        reminder: bool = False,
        reading: bool = False,
        is_editing: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.link_id = link_id
        self.link = link
        self.summary = summary
        self.tags = tags
        self.reminder = reminder
        self.reading = reading
        self.is_editing = is_editing

    def compose(self) -> ComposeResult:
        tag_list = httpx.get(f"{API_HOST}/tags").json()
        yield Container(
            Container(
                Static("Link:"),
                Input(id="links", value=self.link),
                id="link-input-container",
            ),
            Container(
                Static("Summary:"),
                Input(id="summary", value=self.summary),
                id="summary-input-container",
            ),
            Container(
                Static("Tags: " + " ".join(self.tags), id="tag-status"),
                Input(id="tags", suggester=SuggestFromList(tag_list)),
                id="tag-input-container",
            ),
            Horizontal(
                Static("Reminder: ", classes="label"),
                Switch(value=self.reminder, id="reminder"),
                Static("Reading List: ", classes="label"),
                Switch(value=self.reading, id="reading-list"),
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

        if not self.is_editing:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{API_HOST}/link",
                    json={
                        "url": link_value,
                        "summary": summary_value,
                        "tags": self.tags,
                        "reminder": reminder_value,
                        "reading": reading_value,
                    },
                )

            self.dismiss()
            self.tags.clear()

        else:
            async with httpx.AsyncClient() as client:
                await client.patch(
                    f"{API_HOST}/link/{self.link_id}",
                    json={
                        "url": link_value,
                        "summary": summary_value,
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
