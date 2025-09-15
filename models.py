from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class GenerationResponse(BaseModel):
    images_url: List[str]


class GenerationRequest(BaseModel):
    prompts: List[str]


class SequentialImageGeneration(str, Enum):
    DISABLED = "disabled"
    AUTO = "auto"


class ResponseFormat(str, Enum):
    URL = "url"
    B64_JSON = "b64_json"


class ImageSize(str, Enum):
    SIZE_1K = "1K"
    SIZE_2K = "2K"
    SIZE_4K = "4K"


class SequentialImageGenerationOptions(BaseModel):
    max_images: Optional[int] = None


class BytePlusImageRequest(BaseModel):
    model: str = "ep-20250911111250-zd7zw"
    prompt: str
    image: Optional[Union[str, List[str]]] = None  # Single URL or list of URLs for reference images
    sequential_image_generation: SequentialImageGeneration = SequentialImageGeneration.DISABLED
    sequential_image_generation_options: Optional[SequentialImageGenerationOptions] = None
    response_format: ResponseFormat = ResponseFormat.URL
    size: ImageSize = ImageSize.SIZE_2K
    stream: bool = False
    watermark: bool = True


class BytePlusImageResponse(BaseModel):
    data: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None


class StylePlanRequest(BaseModel):
    final_prompt: str | None = None
    style: str | None = None
    modifiers: list[str] | None = None
    target: str | None = None
    constraints: list[str] | None = None
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
