"""
FastAPI Main Application.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from config.settings import settings
from api.routes import router as api_router
from api.openai_compat import router as openai_router

app = FastAPI(
    title="Multi-Agent Web Design Generation & Evaluation System",
    description="Production-quality research prototype implementing closed-loop multi-agent evaluation and refinement of web designs.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(api_router)
app.include_router(openai_router)

# Mount UI static assets
ui_static_dir = Path("./ui/static")
ui_static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(ui_static_dir)), name="static")


@app.get("/", response_class=HTMLResponse, summary="Web Design Research Dashboard")
async def index():
    index_file = Path("./ui/index.html")
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>Multi-Agent Web Design Research System</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/health", summary="Health check endpoint")
async def health_check():
    return {
        "status": "healthy",
        "system_mode": settings.system_mode.value,
        "default_provider": settings.default_provider.value,
    }
