from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from earnetics_crm import models
from earnetics_crm.database import engine
from earnetics_crm.routers import contacts, deals, interactions, tasks, pipelines, insights

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Earnetics CRM", version="1.0.0")

# Allow local UI access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contacts.router)
app.include_router(deals.router)
app.include_router(interactions.router)
app.include_router(tasks.router)
app.include_router(pipelines.router)
app.include_router(insights.router)


@app.get("/crm/health")
def health():
    return {"status": "ok"}
