#!/usr/bin/env python3
"""
Test script for BytePlus image generation endpoint
Demonstrates all 5 use cases from the provided cURL examples
"""

import requests
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8003"

def test_case_1_text2img_single():
    """Test Case 1: Text2Img (single image)"""
    print("🧪 Testing Case 1: Text2Img (single image)")
    
    payload = {
        "model": "ep-20250911111250-zd7zw",
        "prompt": "Interstellar travel, a black hole, from which a nearly shattered vintage train bursts forth, visually striking, cinematic blockbuster, apocalyptic vibe, dynamic, contrasting colors, OC render, ray tracing, motion blur, depth of field, surrealism, deep blue. The image uses delicate and rich color layers to shape the subject and scene, with realistic textures. The dark style background's light and shadow effects create an atmospheric mood, blending artistic fantasy with an exaggerated wide-angle perspective, lens flare, reflections, extreme light and shadow, intense gravitational pull, devouring.",
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2K",
        "stream": False,
        "watermark": True
    }
    
    return make_request(payload)

def test_case_2_text2img_multiple():
    """Test Case 2: Text2Img (multiple images from prompt)"""
    print("🧪 Testing Case 2: Text2Img (multiple images from prompt)")
    
    payload = {
        "model": "ep-20250911111250-zd7zw",
        "prompt": "Generate a series of 4 coherent illustrations focusing on the same corner of a courtyard across the four seasons, presented in a unified style that captures the unique colors, elements, and atmosphere of each season.",
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {
            "max_images": 4
        },
        "response_format": "url",
        "size": "2K",
        "stream": True,
        "watermark": True
    }
    
    return make_request(payload)

def test_case_3_img2img_single():
    """Test Case 3: Img2Img (single reference image)"""
    print("🧪 Testing Case 3: Img2Img (single reference image)")
    
    payload = {
        "model": "ep-20250911111250-zd7zw",
        "prompt": "Generate a close-up image of a dog lying on lush grass.",
        "image": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imageToimage.png",
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2K",
        "stream": False,
        "watermark": True
    }
    
    return make_request(payload)

def test_case_4_img2img_expand():
    """Test Case 4: Img2Img (expand to multiple images)"""
    print("🧪 Testing Case 4: Img2Img (expand to multiple images)")
    
    payload = {
        "model": "ep-20250911111250-zd7zw",
        "prompt": "Using this LOGO as a reference, create a visual design system for an outdoor sports brand named GREEN, including packaging bags, hats, paper boxes, wristbands, lanyards, etc. Main visual tone is green, with a fun, simple, and modern style.",
        "image": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imageToimages.png",
        "sequential_image_generation": "auto",
        "sequential_image_generation_options": {
            "max_images": 5
        },
        "response_format": "url",
        "size": "2K",
        "stream": True,
        "watermark": True
    }
    
    return make_request(payload)

def test_case_5_img2img_multiple_refs():
    """Test Case 5: Img2Img (multiple reference images)"""
    print("🧪 Testing Case 5: Img2Img (multiple reference images)")
    
    payload = {
        "model": "ep-20250911111250-zd7zw",
        "prompt": "Replace the clothing in image 1 with the outfit from image 2.",
        "image": [
            "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimage_1.png",
            "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimage_2.png"
        ],
        "sequential_image_generation": "disabled",
        "response_format": "url",
        "size": "2K",
        "stream": False,
        "watermark": True
    }
    
    return make_request(payload)

def make_request(payload: Dict[str, Any]) -> bool:
    """Make HTTP request to the BytePlus endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/byteplus-generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Generated {len(result.get('data', []))} image(s)")
            for i, img_data in enumerate(result.get('data', [])):
                if 'url' in img_data:
                    print(f"   Image {i+1}: {img_data['url']}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all test cases"""
    print("🚀 Starting BytePlus Image Generation API Tests\n")
    
    test_functions = [
        test_case_1_text2img_single,
        test_case_2_text2img_multiple,
        test_case_3_img2img_single,
        test_case_4_img2img_expand,
        test_case_5_img2img_multiple_refs
    ]
    
    results = []
    for test_func in test_functions:
        print("-" * 60)
        success = test_func()
        results.append(success)
        print()
    
    print("=" * 60)
    print("📊 Test Results Summary:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! The BytePlus endpoint is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the API key and endpoint configuration.")

if __name__ == "__main__":
    main()