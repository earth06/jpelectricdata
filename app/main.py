from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a minimal response for checking that the web server is running."""
    return {"message": "FastAPI web app is running."}
