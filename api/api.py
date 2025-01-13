from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}


@app.post("/save_note")
async def save_note(note: str, tags: list[str]) -> dict:
    return {"note": note}


@app.post("/save_link")
async def save_link(link: str, tags: list[str]) -> dict:
    return {"link": link}
