import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, migrations, benchmark, nilo, auth

app = FastAPI(
    title="ClientShift Migration Engine",
    description="Deterministic AI-Assisted Code Migration & Benchmark Platform",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(migrations.router, prefix="/api", tags=["Migrations"])
app.include_router(benchmark.router, prefix="/api/benchmark", tags=["Benchmark"])
app.include_router(nilo.router, prefix="/api/nilo", tags=["Nilo Assistant"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication v1"])

@app.get("/")
def root():
    return {
        "engine": "ClientShift",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
