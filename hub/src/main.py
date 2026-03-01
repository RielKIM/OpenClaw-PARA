# PARA Hub — FastAPI 서버 진입점 (Phase 2)
from fastapi import FastAPI
from .api.routers import projects, users, fl

app = FastAPI(
    title="PARA Hub",
    description="OpenClaw-PARA 익명화 지식 공유 허브",
    version="0.1.0",
)

app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(users.router,    prefix="/api/v1/users",    tags=["users"])
app.include_router(fl.router,       prefix="/api/v1/fl",       tags=["federated-learning"])
