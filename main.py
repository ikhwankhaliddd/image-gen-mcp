from fastapi import FastAPI, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from models import (
    GenerationRequest,
    GenerationResponse,
    StylePlanRequest,
    StylePlanOutput,
    CharaGeneratorResponse,
    CharaGeneratorRequest,
)
from services import generate_chara_image, create_style_plan
import uvicorn

app = FastAPI(title="Image Generation Agent")


@app.post("/generate", response_model=GenerationResponse)
async def generate_images_endpoint(request: GenerationRequest):
    if not request.prompts or len(request.prompts) == 0:
        raise HTTPException(status_code=400, detail="At least one prompt is required.")

    try:
        generated_images = generate_images_with_seedream(request.prompts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    urls = [img for img in generated_images]

    return GenerationResponse(images_url=urls)


@app.post("/plan", response_model=StylePlanOutput)
async def style_planner(data: StylePlanRequest):
    return create_style_plan(data)


@app.post("/generate-chara", response_model=CharaGeneratorResponse)
async def generate_character_image_with_seededit(request: CharaGeneratorRequest):
    if request.input_image is None:
        output_image_url, seedream_response = generate_chara_image(request)
        return CharaGeneratorResponse(
            output_image_url=output_image_url, seedream_response=seedream_response
        )
    output_image_url, seededit_response = generate_chara_image(request)
    return CharaGeneratorResponse(
        output_image_url=output_image_url, seededit_response=seededit_response
    )


if __name__ == "__main__":
    print("Image Generation Agent is running on port 8003.")
    uvicorn.run(app, host="0.0.0.0", port=8003)
