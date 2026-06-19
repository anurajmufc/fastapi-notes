from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import Base, engine
from routers import notes, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/api/users", tags=["users"])

app.include_router(notes.router, prefix="/api/notes", tags=["notes"])


# Home route


@app.get("/")
async def read_root():
    return "Welcome to my notes API"
