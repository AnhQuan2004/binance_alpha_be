from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import Database
from routes import public, admin, token, alpha_insight


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting up...")
    yield
    # Shutdown
    print("👋 Shutting down...")
    await Database.close()


app = FastAPI(
    title="Airdrop Management API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["ETag", "Last-Modified"],
)


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "invalid_payload", "detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)}
    )


# Include routers
app.include_router(public.router, tags=["Public"])
app.include_router(admin.router, tags=["Admin"])
app.include_router(token.router, tags=["Tokens"])
app.include_router(alpha_insight.router, tags=["Alpha Insights"])


@app.get("/")
async def root():
    return {
        "message": "Airdrop Management API",
        "version": "1.0.0",
        "endpoints": {
            "public": "/api/airdrops?range=today|upcoming|all",
            "admin": "/api/admin/airdrops"
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
