from typing import List
import time

import os
from openai import OpenAI, api_key
import requests
from dotenv import load_dotenv
from models import StylePlanRequest, StylePlanOutput, CharaGeneratorRequest, BytePlusImageRequest, BytePlusImageResponse

# Make sure that you have stored the API Key in the environment variable ARK_API_KEY
# Initialize the Ark client to read your API Key from an environment variable
load_dotenv()

ark_api_key = os.environ.get("ARK_API_KEY")
client = OpenAI(
    # This is the default path. You can configure it based on the service location
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3",
    # Get your Key authentication from the environment variable. This is the default mode and you can modify it as required
    api_key=ark_api_key,
)
model_id = os.environ.get("SEEDREAM_MODEL_ID")


# Placeholder: Replace with actual Seedream API integration
import base64
import json
import re

# Add this import at the top if not already present


def call_seedream_api(prompt: str) -> tuple[bytes, str]:
    """
    Call Seedream Text-to-Image API with reference image.
    This function sends both the reference image (base64) and prompt to Seedream
    and returns the generated image bytes.
    """
    # Use direct API call instead of OpenAI client for image-to-image generation
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}",
    }

    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations",
        json={
            "model": model_id,
            "prompt": f"Generate a high-quality, production-grade product photo of {prompt}",
            "response_format": "url",
            "size": "1024x1024",
            "guidance_scale": 5.5,
            "seed": 42,  # Optional: for reproducible results
            "watermark": False,
        },
        headers=headers,
    )

    if response.status_code == 200:
        result = response.json()
        image_url = result["data"][0]["url"]
        output = requests.get(image_url).content
        return output, image_url
    else:
        raise Exception(
            f"Seedream API request failed with status code {response.status_code}: {response.text}"
        )


def generate_images_with_seedream(prompts: List[str]) -> List[str]:
    generated_images = []
    for prompt in prompts:
        img_bytes, image_url = call_seedream_api(prompt)
        edited_img_bytes, edited_image_url = edit_image_with_seededit(
            img_bytes, image_url, prompt
        )
        generated_images.append(edited_image_url)
    return generated_images


def edit_image_with_seededit(
    image_bytes: bytes, image_url: str, prompt: str
) -> tuple[bytes, str]:
    """
    Use SeedEdit model to refine the generated image.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}",
    }

    # Convert image to base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations",
        json={
            "api_key": ark_api_key,
            "model": "seededit-3-0-i2i-250628",  # Replace with your actual model name
            "prompt": f"Enhance the quality of the image by improving accuracy of packaging or lighting.",
            "image": f"{image_url}",
            "response_format": "url",
            "size": "adaptive",
            "guidance_scale": 1.1,
            "watermark": False,
        },
        headers=headers,
    )

    if response.status_code == 200:
        result = response.json()
        image_url = result["data"][0]["url"]
        edited_image = requests.get(image_url).content
        return edited_image, image_url
    else:
        raise Exception(
            f"SeedEdit API request failed with status code {response.status_code}: {response.text}"
        )


def create_style_plan(data: StylePlanRequest) -> StylePlanOutput:
    """
    Merge identity + style prompt into a ready-to-use SeedEdit payload.
    """
    if data.image_url is None:
        payload = {
            "prompt": data.final_prompt,
            "strength": data.strength,
            "preserve_identity": [f"{item}" for item in data.constraints],
        }
        return StylePlanOutput(
            prompt=data.final_prompt,
            strength=data.strength,
            seedream_payload=payload,
        )
    payload = {
        "input_image": data.image_url,
        "prompt": data.final_prompt,
        "strength": data.strength,
        "preserve_identity": [f"{item}" for item in data.constraints],
    }

    return StylePlanOutput(
        prompt=data.final_prompt,
        strength=data.strength,
        image_url=data.image_url,
        seededit_payload=payload,
    )


def call_seededit_for_chara_style_plan(
    input_image: str, prompt: str
) -> tuple[str, str]:
    """
    Call SeedEdit API for character style plan.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}",
    }
    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations",
        json={
            "api_key": ark_api_key,
            "model": "seededit-3-0-i2i-250628",
            "prompt": prompt,
            "image": input_image,
            "response_format": "url",
            "size": "adaptive",
            "guidance_scale": 1.1,
            "watermark": False,
        },
        headers=headers,
    )
    if response.status_code == 200:
        result = response.json()
        image_url = result["data"][0]["url"]
        return image_url, result


def call_seedream_for_chara_style_plan(prompt: str) -> tuple[str, str]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}",
    }

    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations",
        json={
            "model": model_id,
            "prompt": f"{prompt}",
            "response_format": "url",
            "size": "1024x1024",
            "guidance_scale": 6.0,
            "seed": 42,  # Optional: for reproducible results
            "watermark": False,
        },
        headers=headers,
    )

    if response.status_code == 200:
        result = response.json()
        image_url = result["data"][0]["url"]
        return image_url, result
    else:
        raise Exception(
            f"Seedream API request failed with status code {response.status_code}: {response.text}"
        )


def generate_chara_image(
    request: CharaGeneratorRequest,
) -> tuple[str, str]:
    user_prompt = f"""
    {request.final_prompt}
    Constraints: {request.seededit_payload.get('preserve_identity', [])},
    Strength: {request.strength},
    """
    if request.input_image:
        output_image_url, seededit_response = call_seededit_for_chara_style_plan(
            request.input_image, user_prompt
        )
    else:
        output_image_url, seedream_response = call_seedream_for_chara_style_plan(
            user_prompt
        )
        return output_image_url, seedream_response
        # TODO: 1. Call SeedEdit for Postprocessor
        # TODO: 2. Call Seedance for Image2Vid
    return output_image_url, seededit_response


def _parse_streaming_response(response_text: str) -> BytePlusImageResponse:
    """Parse Server-Sent Events (SSE) response from BytePlus API"""
    images = []
    usage = None
    
    # Split response into event blocks
    events = response_text.strip().split('\n\n')
    
    for event_block in events:
        if not event_block.strip():
            continue
            
        lines = event_block.strip().split('\n')
        event_type = None
        data = None
        
        # Parse event type and data
        for line in lines:
            if line.startswith('event: '):
                event_type = line[7:].strip()
            elif line.startswith('data: '):
                data_str = line[6:].strip()
                # Skip [DONE] marker
                if data_str == '[DONE]':
                    continue
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue
        
        # Process different event types
        if event_type and data:
            if event_type == 'image_generation.partial_succeeded':
                # Extract image information from partial success events
                if 'url' in data and 'size' in data:
                    images.append({
                        "url": data['url'],
                        "size": data['size']
                    })
            elif event_type == 'image_generation.completed':
                # Extract usage information from completion event
                if 'usage' in data:
                    usage = data['usage']
    
    # Ensure usage is always set
    if usage is None:
        usage = {
            "generated_images": len(images),
            "output_tokens": 0,
            "total_tokens": 0
        }
    
    return BytePlusImageResponse(data=images, usage=usage)


def _format_prompt_for_multiple_images(prompt: str, max_images: int) -> str:
    """
    Format prompt for multiple image generation.
    BytePlus API requires explicit 'series' language for multiple image generation to work.
    """
    # Check if prompt already mentions series/multiple images
    series_keywords = ['series', 'illustrations', 'images', 'variations', 'different']
    if any(keyword in prompt.lower() for keyword in series_keywords):
        return prompt
    
    # Format the prompt to explicitly request a series
    formatted_prompt = f"Generate a series of {max_images} coherent illustrations of {prompt}, each showing different perspectives or variations, presented in a unified style."
    
    return formatted_prompt


def generate_byteplus_images(request: BytePlusImageRequest) -> BytePlusImageResponse:
    """
    Comprehensive BytePlus image generation function that handles all 5 use cases:
    1. Text2Img (single image)
    2. Text2Img (multiple images from prompt) 
    3. Img2Img (single reference image)
    4. Img2Img (expand to multiple images)
    5. Img2Img (multiple reference images)
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ark_api_key}",
    }
    
    # Determine if we need to format the prompt for multiple images
    original_prompt = request.prompt
    formatted_prompt = original_prompt
    
    # Check if this is a multiple image generation request
    is_multiple_images = (
        request.sequential_image_generation.value == "auto" and 
        request.sequential_image_generation_options is not None and
        request.sequential_image_generation_options.max_images is not None and
        request.sequential_image_generation_options.max_images > 1
    )
    
    if is_multiple_images:
        max_images = request.sequential_image_generation_options.max_images
        formatted_prompt = _format_prompt_for_multiple_images(original_prompt, max_images)
    
    # Build the request payload
    payload = {
        "model": request.model,
        "prompt": formatted_prompt,
        "sequential_image_generation": request.sequential_image_generation.value,
        "response_format": request.response_format.value,
        "size": request.size.value,
        "stream": request.stream,
        "watermark": request.watermark
    }
    
    # Add image(s) if provided (for Img2Img use cases)
    if request.image is not None:
        payload["image"] = request.image
    
    # Add sequential image generation options if provided
    if request.sequential_image_generation_options is not None:
        payload["sequential_image_generation_options"] = {
            "max_images": request.sequential_image_generation_options.max_images
        }
    
    # Make the API call
    response = requests.post(
        "https://ark.ap-southeast.bytepluses.com/api/v3/images/generations",
        json=payload,
        headers=headers,
    )
    
    if response.status_code == 200:
        # Handle streaming response (when stream=True)
        if 'text/event-stream' in response.headers.get('content-type', ''):
            return _parse_streaming_response(response.text)
        else:
            # Handle regular JSON response (when stream=False)
            result = response.json()
            return BytePlusImageResponse(**result)
    else:
        raise Exception(
            f"BytePlus API request failed with status code {response.status_code}: {response.text}"
        )
