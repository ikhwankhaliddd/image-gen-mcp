# Custom Page Icon Guide

This guide shows different ways to use custom images as Streamlit page icons.

## Current Implementation

The app now uses a custom SVG icon located at `assets/app_icon.svg`:

```python
st.set_page_config(
    page_title="BytePlus Image Generation MCP",
    page_icon="assets/app_icon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

## Alternative Icon Options

### 1. Using PNG/JPG Images
```python
# For PNG or JPG files
st.set_page_config(
    page_icon="assets/icon.png",  # or .jpg
    # ... other config
)
```

### 2. Using ICO Files (Recommended for favicons)
```python
# For ICO files (traditional favicon format)
st.set_page_config(
    page_icon="assets/favicon.ico",
    # ... other config
)
```

### 3. Using Base64 Encoded Images
```python
import base64

# Convert image to base64
with open("assets/icon.png", "rb") as f:
    icon_base64 = base64.b64encode(f.read()).decode()

st.set_page_config(
    page_icon=f"data:image/png;base64,{icon_base64}",
    # ... other config
)
```

### 4. Using PIL Image Objects
```python
from PIL import Image

# Load image with PIL
icon_image = Image.open("assets/icon.png")

st.set_page_config(
    page_icon=icon_image,
    # ... other config
)
```

### 5. Using Emoji (Original approach)
```python
st.set_page_config(
    page_icon="🎨",  # Any emoji
    # ... other config
)
```

## Icon Requirements

- **Size**: Recommended 32x32 pixels or 16x16 pixels
- **Format**: SVG, PNG, JPG, ICO, or emoji
- **Location**: Place in `assets/` folder or any accessible path
- **Browser Cache**: May need to clear browser cache to see changes

## Current Custom Icon Features

The current SVG icon includes:
- Purple gradient background representing creativity
- Image frame with landscape scene
- Sparkle effects suggesting AI generation
- Scalable vector format for crisp display at any size

## Changing the Icon

To use a different image:

1. Place your image file in the `assets/` folder
2. Update the `page_icon` parameter in `streamlit_app.py`
3. Restart the Streamlit app if needed
4. Clear browser cache if the old icon persists

Example:
```python
st.set_page_config(
    page_icon="assets/your_custom_icon.png",
    # ... other config
)
```