from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes.task_routes import router as task_router
from app.routes import admin_routes
from app.routes import auth_routes
from app.routes.qa_routes import router as qa_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Manager API")

# CORS - allow frontend dev server
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)
app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(qa_router)


@app.get("/")
def root():
    return {"message": "Task Manager API is running"}


