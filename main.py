from fastapi import FastAPI, HTTPException
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
from models import GenerationRequest, GenerationResponse
from services import generate_images_with_seedream
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


if __name__ == "__main__":
    print("Image Generation Agent is running on port 8003.")
    uvicorn.run(app, host="0.0.0.0", port=8003)
