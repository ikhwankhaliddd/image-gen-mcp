from pydantic import BaseModel
from typing import List


class GenerationResponse(BaseModel):
    images_url: List[str]


class GenerationRequest(BaseModel):
    prompts: List[str]
