from typing import List
import time

import os
from openai import OpenAI, api_key
import requests
from dotenv import load_dotenv
from models import StylePlanRequest, StylePlanOutput, CharaGeneratorRequest

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
