from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine
from routers import applications, users


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/api/users", tags=["users"])

app.include_router(applications.router, prefix="/api/applications", tags=["applications"])


# Home route


@app.get("/")
async def read_root():
    return "Welcome to my Job Application Tracker API"
