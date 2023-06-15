from backend.create_app import create_app

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.asgi:app", host="localhost", port=8000, reload=True)
