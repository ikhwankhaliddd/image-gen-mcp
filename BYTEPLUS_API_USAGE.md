# BytePlus Image Generation API

This endpoint provides a comprehensive solution for all BytePlus image generation use cases, consolidating the 5 different cURL examples into a single, flexible endpoint.

## Endpoint

```
POST /byteplus-generate
```

## Request Schema

```json
{
  "model": "ep-20250911111250-zd7zw",
  "prompt": "string",
  "image": "string | array of strings (optional)",
  "sequential_image_generation": "disabled | auto",
  "sequential_image_generation_options": {
    "max_images": "integer (optional)"
  },
  "response_format": "url | b64_json",
  "size": "1K | 2K | 4K",
  "stream": "boolean",
  "watermark": "boolean"
}
```

## Use Cases

### 1. Text2Img (Single Image)

Generate a single image from text prompt.

```bash
curl -X POST "http://localhost:8003/byteplus-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ep-20250911111250-zd7zw",
    "prompt": "Interstellar travel, a black hole, from which a nearly shattered vintage train bursts forth, visually striking, cinematic blockbuster, apocalyptic vibe, dynamic, contrasting colors, OC render, ray tracing, motion blur, depth of field, surrealism, deep blue.",
    "sequential_image_generation": "disabled",
    "response_format": "url",
    "size": "2K",
    "stream": false,
    "watermark": true
  }'
```

### 2. Text2Img (Multiple Images from Prompt)

Generate multiple coherent images from a single prompt.

```bash
curl -X POST "http://localhost:8003/byteplus-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ep-20250911111250-zd7zw",
    "prompt": "Generate a series of 4 coherent illustrations focusing on the same corner of a courtyard across the four seasons, presented in a unified style that captures the unique colors, elements, and atmosphere of each season.",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {
      "max_images": 4
    },
    "response_format": "url",
    "size": "2K",
    "stream": true,
    "watermark": true
  }'
```

### 3. Img2Img (Single Reference Image)

Generate an image based on a text prompt and a single reference image.

```bash
curl -X POST "http://localhost:8003/byteplus-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ep-20250911111250-zd7zw",
    "prompt": "Generate a close-up image of a dog lying on lush grass.",
    "image": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imageToimage.png",
    "sequential_image_generation": "disabled",
    "response_format": "url",
    "size": "2K",
    "stream": false,
    "watermark": true
  }'
```

### 4. Img2Img (Expand to Multiple Images)

Generate multiple images based on a single reference image.

```bash
curl -X POST "http://localhost:8003/byteplus-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ep-20250911111250-zd7zw",
    "prompt": "Using this LOGO as a reference, create a visual design system for an outdoor sports brand named GREEN, including packaging bags, hats, paper boxes, wristbands, lanyards, etc. Main visual tone is green, with a fun, simple, and modern style.",
    "image": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imageToimages.png",
    "sequential_image_generation": "auto",
    "sequential_image_generation_options": {
      "max_images": 5
    },
    "response_format": "url",
    "size": "2K",
    "stream": true,
    "watermark": true
  }'
```

### 5. Img2Img (Multiple Reference Images)

Generate an image using multiple reference images.

```bash
curl -X POST "http://localhost:8003/byteplus-generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ep-20250911111250-zd7zw",
    "prompt": "Replace the clothing in image 1 with the outfit from image 2.",
    "image": [
      "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimage_1.png",
      "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/seedream4_imagesToimage_2.png"
    ],
    "sequential_image_generation": "disabled",
    "response_format": "url",
    "size": "2K",
    "stream": false,
    "watermark": true
  }'
```

## Response Schema

```json
{
  "data": [
    {
      "url": "string",
      "b64_json": "string (if response_format is b64_json)"
    }
  ],
  "usage": {
    "prompt_tokens": "integer",
    "completion_tokens": "integer",
    "total_tokens": "integer"
  }
}
```

## Configuration

Make sure to set the following environment variables:

```bash
export ARK_API_KEY="your_byteplus_api_key"
export SEEDREAM_MODEL_ID="ep-20250911111250-zd7zw"
```

## Running the Server

```bash
python main.py
```

The server will start on `http://localhost:8003`.

## Testing

Use the provided test script to verify all use cases:

```bash
python test_byteplus_endpoint.py
```

## Key Features

- **Unified Endpoint**: Single endpoint handles all 5 use cases
- **Type Safety**: Full Pydantic validation for requests and responses
- **Flexible Image Input**: Supports single image URL, multiple image URLs, or no image
- **Sequential Generation**: Supports both single and multiple image generation
- **Streaming Support**: Optional streaming for real-time results
- **Error Handling**: Comprehensive error handling with meaningful messages

## Implementation Details

The endpoint automatically determines the use case based on the provided parameters:

- **Text2Img**: When no `image` field is provided
- **Img2Img**: When `image` field contains URL(s)
- **Single vs Multiple**: Controlled by `sequential_image_generation` and `max_images`
- **Reference Images**: Single string for one image, array for multiple images