from pydantic import BaseModel
from typing import List


class GenerationResponse(BaseModel):
    images_base64: List[str]


class GenerationRequest(BaseModel):
    prompts: List[str]
