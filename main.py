from fastapi import FastAPI, HTTPException, Query
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse, Response
from typing import List
import requests
import base64
import io
from PIL import Image
from models import (
    GenerationRequest,
    GenerationResponse,
    StylePlanRequest,
    StylePlanOutput,
    CharaGeneratorResponse,
    CharaGeneratorRequest,
    BytePlusImageRequest,
    BytePlusImageResponse,
)
from services import generate_chara_image, create_style_plan, generate_byteplus_images
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


@app.post("/byteplus-generate", response_model=BytePlusImageResponse)
async def byteplus_image_generation(request: BytePlusImageRequest):
    """
    Comprehensive BytePlus image generation using Seedream 4.0 API endpoint that supports all 5 use cases:
    
    1. Text2Img (single image): 
       - Set sequential_image_generation="disabled"
       - Don't provide image field
    
    2. Text2Img (multiple images from prompt):
       - Set sequential_image_generation="auto" 
       - Set sequential_image_generation_options.max_images
       - Don't provide image field
    
    3. Img2Img (single reference image):
       - Set sequential_image_generation="disabled"
       - Provide single image URL in image field
    
    4. Img2Img (expand to multiple images):
       - Set sequential_image_generation="auto"
       - Set sequential_image_generation_options.max_images
       - Provide single image URL in image field
    
    5. Img2Img (multiple reference images):
       - Set sequential_image_generation="disabled" 
       - Provide list of image URLs in image field
    """
    try:
        result = generate_byteplus_images(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/byteplus-generate-image")
async def byteplus_image_generation_direct(
    request: BytePlusImageRequest,
    image_index: int = Query(0, description="Index of the image to return (default: 0)")
):
    """
    Generate images using BytePlus API and return the actual image data instead of JSON.
    Returns the first image by default, or specify image_index for other images.
    
    This endpoint returns the image with proper Content-Type headers for direct browser rendering.
    """
    try:
        # Get the JSON response first
        result = generate_byteplus_images(request)
        
        # Check if we have any images
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="No images generated")
        
        # Validate image index
        if image_index >= len(result.data):
            raise HTTPException(
                status_code=400, 
                detail=f"Image index {image_index} out of range. Available images: 0-{len(result.data)-1}"
            )
        
        image_data = result.data[image_index]
        
        # Handle different image data formats
        if 'url' in image_data:
            # Download image from URL
            image_url = image_data['url']
            response = requests.get(image_url)
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to download image from URL")
            
            image_bytes = response.content
            content_type = response.headers.get('content-type', 'image/png')
            
        elif 'b64_json' in image_data:
            # Decode base64 image
            try:
                image_bytes = base64.b64decode(image_data['b64_json'])
                content_type = 'image/png'  # Default to PNG for base64 images
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to decode base64 image: {str(e)}")
        
        else:
            raise HTTPException(status_code=500, detail="No valid image data found")
        
        # Validate that we have valid image data
        try:
            # Try to open with PIL to validate it's a valid image
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            
            # Reset the bytes stream since verify() consumes it
            image_bytes = io.BytesIO(image_bytes).getvalue()
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Invalid image data: {str(e)}")
        
        # Return the image with proper headers
        return Response(
            content=image_bytes,
            media_type=content_type,
            headers={
                "Content-Disposition": f"inline; filename=generated_image_{image_index}.png",
                "Cache-Control": "no-cache",
                "X-Image-Index": str(image_index),
                "X-Total-Images": str(len(result.data))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Image Generation Agent is running on port 8003.")
    # Configure uvicorn with longer timeouts for multiple image generation
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8003,
        timeout_keep_alive=300,  # 5 minutes keep-alive timeout
        timeout_graceful_shutdown=30,  # 30 seconds graceful shutdown
        # Add worker timeout for handling long requests
        workers=1  # Single worker to avoid timeout issues
    )
