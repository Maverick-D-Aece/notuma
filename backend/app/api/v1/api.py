from fastapi import APIRouter
from backend.app.api.v1.endpoints import ingest, narrative, image, composition, project

api_router = APIRouter()

# Registering endpoints
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(narrative.router, prefix="/narrative", tags=["narrative"])
api_router.include_router(image.router, prefix="/image", tags=["image"])
api_router.include_router(composition.router, prefix="/composition", tags=["composition"])
api_router.include_router(project.router, prefix="/project", tags=["project"])

@api_router.get("/health-check")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
