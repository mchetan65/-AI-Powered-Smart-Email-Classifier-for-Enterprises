from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .api_routes import email_triage
import os

app = FastAPI(title="Signal Triage API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(email_triage.router, prefix="/api", tags=["Email Triage"])

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Signal Triage API"}

# Serve static UI bundle - mount last to avoid shadowing API routes.
static_dir = os.path.join(os.path.dirname(__file__), "web_bundle")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
