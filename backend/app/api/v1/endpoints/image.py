from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.services.image_generation import ModelHub

router = APIRouter()

class ImageGenerationRequest(BaseModel):
    provider: str = "pollinations"
    prompt: str
    character_traits: Optional[List[str]] = None
    style_features: Optional[Dict[str, Any]] = None
    api_key: Optional[str] = None # For BYOK support

class StyleExtractionRequest(BaseModel):
    url: str

@router.post("/generate-panel")
async def generate_panel(request: ImageGenerationRequest):
    hub = ModelHub({request.provider: request.api_key} if request.api_key else None)

    image_url = hub.generate_panel(
        provider_name=request.provider,
        prompt=request.prompt,
        character_traits=request.character_traits,
        style_features=request.style_features
    )

    if not image_url:
        raise HTTPException(status_code=500, detail="Failed to generate image")

    return {"image_url": image_url}

@router.post("/extract-style")
async def extract_style(request: StyleExtractionRequest):
    style_features = ModelHub.extract_style_from_url(request.url)
    return {"style_features": style_features}

@router.get("/providers")
async def list_providers():
    return {
        "providers": ["pollinations", "openai", "stability", "replicate", "nanobanana"]
    }
