from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}
