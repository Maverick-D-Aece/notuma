from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.services.image_generation import ModelHub
from backend.app.database import get_db
from backend.app.utils.usage_tracker import log_usage
from backend.app.utils.rate_limit import limiter

router = APIRouter()

class ImageGenerationRequest(BaseModel):
    provider: str = "pollinations"
    prompt: str
    character_traits: Optional[List[str]] = None
    style_features: Optional[Dict[str, Any]] = None
    api_key: Optional[str] = None # For BYOK support
    user_id: Optional[str] = None # Optional for usage tracking
    project_id: Optional[str] = None # Optional for usage tracking

class StyleExtractionRequest(BaseModel):
    url: str

@router.post("/generate-panel")
@limiter.limit("10/minute")
async def generate_panel(request: Request, body: ImageGenerationRequest, db: Session = Depends(get_db)):
    hub = ModelHub({body.provider: body.api_key} if body.api_key else None)

    image_url = hub.generate_panel(
        provider_name=body.provider,
        prompt=body.prompt,
        character_traits=body.character_traits,
        style_features=body.style_features
    )

    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to generate image")

    # Log Usage
    log_usage(
        db,
        user_id=body.user_id,
        project_id=body.project_id,
        service="image_generation",
        provider=body.provider,
        metric="images",
        amount=1
    )

    return {"image_url": image_url}

@router.post("/extract-style")
@limiter.limit("5/minute")
async def extract_style(request: Request, body: StyleExtractionRequest):
    style_features = ModelHub.extract_style_from_url(body.url)
    return {"style_features": style_features}

@router.get("/providers")
async def list_providers():
    return {
        "providers": ["pollinations", "openai", "stability", "replicate", "nanobanana"]
    }

@router.get("/usage")
async def get_usage(user_id: Optional[str] = None, db: Session = Depends(get_db)):
    # Simple usage aggregation endpoint
    from backend.app.models import UsageLog
    from sqlalchemy import func

    query = db.query(
        UsageLog.service,
        UsageLog.provider,
        func.sum(UsageLog.amount).label("total_amount")
    )

    if user_id:
        query = query.filter(UsageLog.user_id == user_id)

    results = query.group_by(UsageLog.service, UsageLog.provider).all()

    return [
        {
            "service": r.service,
            "provider": r.provider,
            "total_amount": r.total_amount
        } for r in results
    ]
