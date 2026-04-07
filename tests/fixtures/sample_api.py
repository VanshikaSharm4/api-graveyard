from fastapi import FastAPI
app = FastAPI()

@app.get("/api/users")
def get_users():
    """Returns all users."""
    return []

@app.post("/api/users")
def create_user():
    return {}

@app.get("/api/legacy/data", deprecated=True)
def get_legacy_data():
    return {}

@app.delete("/api/internal/flush")
def flush_cache():
    # no docstring here intentionally
    pass