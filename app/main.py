from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import strings
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown

app = FastAPI(title="String Analyzer API", lifespan=lifespan)

# Include routers
app.include_router(strings.router)

@app.get("/")
def root():
    return {"message": "Welcome to the String Analyzer API!"}
