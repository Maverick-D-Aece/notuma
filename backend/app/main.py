from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.api import api_router
from backend.app.utils.monitoring import setup_monitoring
from backend.app.utils.rate_limit import setup_rate_limiting

# Initialize monitoring
setup_monitoring()

app = FastAPI(
    title="NoTuMa API",
    description="Novel To Manga Converter API",
    version="1.0.0"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiting
setup_rate_limiting(app)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to NoTuMa API", "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
