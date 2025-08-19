from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class GenerationResponse(BaseModel):
    images_url: List[str]


class GenerationRequest(BaseModel):
    prompts: List[str]


class StylePlanRequest(BaseModel):
    final_prompt: str
    style: str
    modifiers: list[str]
    target: str
    constraints: list[str]
    strength: str | None = None
    image_url: str | None = None


class StylePlanOutput(BaseModel):
    prompt: str
    strength: float
    identity_id: Optional[str] = None
    image_url: str | None = None
    seedream_payload: Dict[str, Any] = {}
    seededit_payload: Dict[str, Any] = {}


class CharaGeneratorRequest(BaseModel):
    input_image: str | None = None  # original photo URL
    final_prompt: str  # prompt from style_planner
    identity_id: Optional[str] = None
    strength: float = 0.8  # img2img strength
    seededit_payload: Dict[str, Any] = {}


class CharaGeneratorResponse(BaseModel):
    output_image_url: str  # URL of generated image
    seededit_response: Any | None = None  # raw response from SeedEdit API
    seedream_response: Any | None = None  # raw response from Seedream API
