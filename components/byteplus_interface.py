"""
BytePlus Generation Interface Component
======================================

Interactive controls and interface for BytePlus image generation with all 5 use cases:
1. Text2Img (Single Image)
2. Text2Img (Multiple Images) 
3. Img2Img (Single Reference)
4. Img2Img (Multiple References)
5. Img2Img (Expand to Multiple)
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from PIL import Image
import io
import base64
from datetime import datetime
from components.performance_metrics import log_api_performance
from .responsive_layout import (
    ResponsiveLayout, ErrorHandler, render_responsive_image_grid,
    render_responsive_metrics, safe_execute, validate_inputs,
    show_validation_errors, add_notification, with_error_handling
)

def render_byteplus_generation_interface(mcp):
    """
    Render the complete BytePlus generation interface with interactive controls
    
    Args:
        mcp: MCPInterface instance for API calls and metrics
    """
    
    # Validate mcp parameter
    if mcp is None:
        st.error("❌ MCP interface not available")
        return
    
    # Check if mcp has required attributes
    if not hasattr(mcp, 'endpoints') or not hasattr(mcp, 'update_metrics'):
        st.error("❌ MCP interface is not properly initialized")
        return
    
    # Initialize error handler
    error_handler = ErrorHandler()
    
    # Initialize generation stats if not exists
    if 'generation_stats' not in st.session_state:
        st.session_state.generation_stats = {
            'total_images': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'success_rate': 0.0
        }
    
    st.markdown("### 🎨 BytePlus Image Generation")
    st.markdown("Generate high-quality images using BytePlus AI models")
    
    # Quick stats in responsive layout
    col1, col2 = ResponsiveLayout.create_responsive_columns("stats", min_cols=1, max_cols=2)
    
    with col1:
        if 'generation_stats' in st.session_state:
            stats = st.session_state.generation_stats
            st.metric("Total Generated", stats.get('total_images', 0))
    
    with col2:
        if 'generation_stats' in st.session_state:
            stats = st.session_state.generation_stats
            st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    
    # Main interface tabs
    tab1, tab2, tab3 = st.tabs([
    "🎨 Generate", 
    "⚙️ Advanced Settings", 
    "📊 Results"])
    
    with tab1:
        # Basic generation controls with responsive layout
        # prompt = st.text_area(
        #     "Prompt",
        #     placeholder="Describe the image you want to generate...",
        #     height=100,
        #     help="Detailed description of the image you want to create"
        # )
        
        # # Responsive layout for basic parameters
        # param_cols = ResponsiveLayout.create_responsive_columns("controls", min_cols=2, max_cols=3)
        
        # with param_cols[0]:
        #     size = st.selectbox(
        #         "Image Size",
        #         ["1K", "2K", "4K"],
        #         index=1,
        #         key="main_image_size",
        #         help="Resolution of the generated image"
        #     )
        
        # with param_cols[1]:
        #     num_images = st.number_input(
        #         "Number of Images",
        #         min_value=1,
        #         max_value=10,
        #         value=1,
        #         key="main_num_images",
        #         help="How many images to generate"
        #     )
        
        # if len(param_cols) > 2:
        #     with param_cols[2]:
        #         style = st.selectbox(
        #             "Style",
        #             ["Realistic", "Artistic", "Anime", "Abstract", "Photographic"],
        #             key="main_style_multi_col",
        #             help="Visual style for the generated image"
        #         )
        # else:
        #     style = st.selectbox(
        #         "Style",
        #         ["Realistic", "Artistic", "Anime", "Abstract", "Photographic"],
        #         key="main_style_single_col",
        #         help="Visual style for the generated image"
        #     )
        
        render_generation_controls(mcp)
    
    with tab2:
        render_advanced_settings()
    
    with tab3:
        render_results_panel()

def render_generation_controls(mcp):
    """Render the main generation controls"""
    
    st.markdown("### 🎯 Generation Type")
    
    # Generation type selection
    generation_type = st.selectbox(
        "Choose generation type",
        [
            "Text2Img (Single Image)",
            "Text2Img (Multiple Images)",
            "Img2Img (Single Reference)",
            "Img2Img (Multiple References)", 
            "Img2Img (Expand to Multiple)"
        ],
        key="generation_type_selector",
        help="Select the type of image generation you want to perform"
    )
    
    st.markdown("---")
    
    # Common parameters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Prompt")
        
        # Show helpful tip for multiple image generation
        if "Multiple" in generation_type:
            st.info(
                "💡 **Tip for Multiple Images**: For best results, explicitly request multiple images in your prompt. "
                "Examples:\n"
                "- 'Generate a series of 4 illustrations of...'\n"
                "- 'Create multiple coherent images showing...'\n"
                "- 'Generate 3 different variations of...'"
            )
        
        prompt = st.text_area(
            "Enter your prompt",
            placeholder="Describe the image you want to generate..." if "Multiple" not in generation_type 
                       else "Generate a series of coherent illustrations of...",
            height=100,
            help="Detailed description of the image you want to create"
        )
        
        # Negative prompt
        negative_prompt = st.text_area(
            "Negative prompt (optional)",
            placeholder="What you don't want in the image...",
            height=60,
            help="Describe what you want to avoid in the generated image"
        )
    
    with col2:
        st.markdown("### 🎛️ Basic Settings")
        
        # Image size
        size = st.selectbox(
            "Image Size",
            ["1K", "2K", "4K"],
            index=1,
            key="controls_image_size",
            help="Resolution of the generated image"
        )
        
        # Sequential generation setting
        if "Multiple" in generation_type:
            sequential_mode = st.selectbox(
                "Sequential Generation",
                ["auto", "disabled"],
                index=0,
                key="sequential_mode_selector",
                help="Enable for coherent multi-image generation"
            )
        else:
            sequential_mode = "disabled"
        
        # Number of images for multiple generation
        if "Multiple" in generation_type:
            num_images = st.slider(
                "Number of Images",
                min_value=2,
                max_value=8,
                value=4,
                help="How many images to generate"
            )
        else:
            num_images = 1
    
    # Image upload section for Img2Img
    if "Img2Img" in generation_type:
        st.markdown("---")
        render_image_upload_section(generation_type)
    
    # Generation button and results
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Input validation
        validation_errors = validate_inputs(
            prompt=prompt,
            generation_type=generation_type,
            size=size,
            num_images=num_images
        )
        
        # Show validation errors if any
        if validation_errors:
            show_validation_errors(validation_errors)
        
        # Generate button
        generate_disabled = bool(validation_errors) or not prompt.strip()
        
        if st.button(
            "🚀 Generate Images", 
            type="primary", 
            use_container_width=True,
            disabled=generate_disabled
        ):
            error_handler = ErrorHandler()
            with error_handler.error_boundary("Image Generation"):
                if not prompt.strip():
                    st.error("Please enter a prompt!")
                    return
                
                # Validate image uploads for Img2Img
                if "Img2Img" in generation_type:
                    uploaded_images = st.session_state.get('uploaded_images', [])
                    if not uploaded_images:
                        st.error("Please upload reference images for Img2Img generation!")
                        return
                
                # Get current widget values from session state to ensure we have the latest values
                current_sequential_mode = st.session_state.get('sequential_mode_selector', 'auto') if "Multiple" in generation_type else "disabled"
                
                # Prepare request data
                request_data = prepare_request_data(
                    generation_type, prompt, negative_prompt, size, 
                    current_sequential_mode, num_images
                )
                
                # Determine which API endpoint to use based on response format setting
                use_direct_image = False
                if 'advanced_settings' in st.session_state:
                    response_format = st.session_state.advanced_settings.get('response_format', 'JSON (Standard)')
                    use_direct_image = response_format == 'Direct Image'
                
                # Show response format info
                if use_direct_image:
                    st.info("🖼️ Using Direct Image response format - returning actual image data")
                else:
                    st.info("📄 Using JSON response format - returning image URLs/base64")
                
                # Make API call with error handling
                with st.spinner("Generating images... This may take a few moments."):
                    if use_direct_image:
                        api_result = safe_execute(
                            make_direct_image_request,
                            mcp,
                            request_data,
                            0,  # image_index
                            operation_name="Direct Image Generation API Call"
                        )
                    else:
                        api_result = safe_execute(
                            make_generation_request,
                            mcp,
                            request_data,
                            operation_name="Image Generation API Call"
                        )

                    
                    # Handle the result safely
                    if api_result and isinstance(api_result, tuple) and len(api_result) == 2:
                        success, result = api_result
                        if success:
                            st.success("✅ Images generated successfully!")
                            add_notification("Images generated successfully!", "success")
                            
                            # Store result in session state for results panel
                            if 'generation_results' not in st.session_state:
                                st.session_state.generation_results = []
                            
                            st.session_state.generation_results.append({
                                'timestamp': datetime.now(),
                                'type': generation_type,
                                'prompt': prompt,
                                'result': result,
                                'settings': {
                                    'size': size,
                                    'sequential_mode': current_sequential_mode,
                                    'num_images': num_images
                                }
                            })
                            
                            # Display images immediately
                            display_generation_results(result)
                            
                            # Update generation stats
                            update_generation_stats(True, num_images)
                        else:
                            error_msg = result if isinstance(result, str) else "Generation request failed"
                            st.error(f"❌ Generation failed: {error_msg}")
                            add_notification(f"Generation failed: {error_msg}", "error")
                            update_generation_stats(False, 0)
                    else:
                        st.error("❌ Generation failed: Invalid response from server")
                        add_notification("Generation failed: Invalid response from server", "error")
                        update_generation_stats(False, 0)

def render_image_upload_section(generation_type: str):
    """Render image upload section for Img2Img generation"""
    
    st.markdown("### 🖼️ Reference Images")
    
    if "Multiple References" in generation_type:
        st.info("💡 Upload multiple reference images (2-4 recommended)")
        max_files = 4
    else:
        st.info("💡 Upload a single reference image")
        max_files = 1
    
    uploaded_files = st.file_uploader(
        "Choose image files",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=(max_files > 1),
        help=f"Upload up to {max_files} reference images"
    )
    
    # Process uploaded images
    if uploaded_files:
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        
        if len(uploaded_files) > max_files:
            st.warning(f"⚠️ Too many files! Please upload maximum {max_files} images.")
            uploaded_files = uploaded_files[:max_files]
        
        # Display uploaded images
        cols = st.columns(min(len(uploaded_files), 4))
        processed_images = []
        
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                # Convert to base64 for API
                image_bytes = uploaded_file.read()
                image_b64 = base64.b64encode(image_bytes).decode()
                processed_images.append(f"data:image/{uploaded_file.type.split('/')[-1]};base64,{image_b64}")
                
                # Display thumbnail
                with cols[idx % 4]:
                    image = Image.open(io.BytesIO(image_bytes))
                    st.image(image, caption=f"Image {idx+1}", use_column_width=True)
                    
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        # Store processed images in session state
        st.session_state.uploaded_images = processed_images
        st.success(f"✅ {len(processed_images)} image(s) uploaded successfully!")
    else:
        st.session_state.uploaded_images = []

def render_advanced_settings():
    """Render advanced generation settings"""
    
    st.markdown("### 🔧 Advanced Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Model Settings")
        
        # Model selection (if multiple models available)
        model = st.selectbox(
            "Model",
            ["seedream-v4", "seedream-v3"],
            key="advanced_model_selector",
            help="Choose the generation model"
        )
        
        # Guidance scale
        guidance_scale = st.slider(
            "Guidance Scale",
            min_value=1.0,
            max_value=20.0,
            value=7.5,
            step=0.5,
            help="How closely to follow the prompt (higher = more adherence)"
        )
        
        # Steps
        steps = st.slider(
            "Generation Steps",
            min_value=10,
            max_value=100,
            value=50,
            step=5,
            help="Number of denoising steps (higher = better quality, slower)"
        )
    
    with col2:
        st.markdown("#### Output Settings")
        
        # Seed for reproducibility
        use_seed = st.checkbox("Use fixed seed", help="Enable for reproducible results")
        if use_seed:
            seed = st.number_input(
                "Seed",
                min_value=0,
                max_value=2**32-1,
                value=42,
                help="Random seed for reproducible generation"
            )
        else:
            seed = None
        
        # Response format
        response_format = st.selectbox(
            "Response Format",
            ["JSON (Standard)", "Direct Image"],
            key="advanced_response_format",
            help="Choose how the API returns image data"
        )
        
        # Output format
        output_format = st.selectbox(
            "Output Format",
            ["PNG", "JPEG", "WEBP"],
            key="advanced_output_format",
            help="Image output format"
        )
        
        # Quality (for JPEG)
        if output_format == "JPEG":
            quality = st.slider(
                "JPEG Quality",
                min_value=50,
                max_value=100,
                value=95,
                help="JPEG compression quality"
            )
        else:
            quality = None
    
    # Store advanced settings in session state
    st.session_state.advanced_settings = {
        'model': model,
        'guidance_scale': guidance_scale,
        'steps': steps,
        'seed': seed,
        'response_format': response_format,
        'output_format': output_format.lower(),
        'quality': quality
    }
    
    # Reset to defaults button
    if st.button("🔄 Reset to Defaults"):
        if 'advanced_settings' in st.session_state:
            del st.session_state.advanced_settings
        st.rerun()

def render_results_panel():
    """Render the results panel showing generation history and outputs"""
    
    st.markdown("### 📊 Generation Results")
    
    if 'generation_results' not in st.session_state or not st.session_state.generation_results:
        st.info("No generation results yet. Generate some images to see them here!")
        return
    
    # Results filter and sorting
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        filter_type = st.selectbox(
            "Filter by type",
            ["All"] + [result['type'] for result in st.session_state.generation_results],
            key="results_filter_type",
            help="Filter results by generation type"
        )
    
    with col2:
        sort_order = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First"],
            key="results_sort_order",
            help="Sort results by timestamp"
        )
    
    with col3:
        if st.button("🗑️ Clear History"):
            st.session_state.generation_results = []
            st.rerun()
    
    # Filter and sort results
    results = st.session_state.generation_results.copy()
    
    if filter_type != "All":
        results = [r for r in results if r['type'] == filter_type]
    
    if sort_order == "Oldest First":
        results.reverse()
    
    # Display results
    for idx, result in enumerate(results):
        with st.expander(
            f"🎨 {result['type']} - {result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
            expanded=(idx == 0)
        ):
            # Result metadata
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Prompt:** {result['prompt']}")
                st.markdown(f"**Type:** {result['type']}")
            
            with col2:
                settings = result['settings']
                st.markdown(f"**Size:** {settings['size']}")
                st.markdown(f"**Images:** {settings['num_images']}")
                if settings['sequential_mode'] != 'disabled':
                    st.markdown(f"**Sequential:** {settings['sequential_mode']}")
            
            # Display generated images
            if 'result' in result and result['result']:
                display_generation_results(result['result'])

def prepare_request_data(generation_type: str, prompt: str, negative_prompt: str, 
                        size: str, sequential_mode: str, num_images: int) -> Dict[str, Any]:
    """Prepare request data for API call"""
    
    request_data = {
        "prompt": prompt,
        "size": size,
        "sequential_image_generation": sequential_mode
    }
    
    # Add negative prompt if provided
    if negative_prompt.strip():
        request_data["negative_prompt"] = negative_prompt
    
    # Add images for Img2Img
    if "Img2Img" in generation_type:
        uploaded_images = st.session_state.get('uploaded_images', [])
        if uploaded_images:
            request_data["image"] = uploaded_images
    
    # Add sequential generation options for multiple images
    if "Multiple" in generation_type:
        request_data["sequential_image_generation_options"] = {
            "max_images": num_images
        }
    
    # Add advanced settings if available
    if 'advanced_settings' in st.session_state:
        advanced = st.session_state.advanced_settings
        if advanced.get('seed') is not None:
            request_data["seed"] = advanced['seed']
        if advanced.get('guidance_scale'):
            request_data["guidance_scale"] = advanced['guidance_scale']
        if advanced.get('steps'):
            request_data["steps"] = advanced['steps']
    
    return request_data

def make_generation_request(mcp, request_data: Dict[str, Any]) -> Tuple[bool, Any]:
    """Make API request for image generation with performance logging"""
    
    start_time = time.time()
    
    try:
        # Calculate request size
        request_size = len(json.dumps(request_data).encode('utf-8'))
        
        # Use longer timeout for multiple image generation
        is_multiple_generation = "sequential_image_generation_options" in request_data
        timeout_duration = 300 if is_multiple_generation else 120  # 5 minutes for multiple, 2 minutes for single
        
        response = requests.post(
            mcp.endpoints['byteplus_generate'],
            json=request_data,
            timeout=timeout_duration
        )
        
        response_time = time.time() - start_time
        success = response.status_code == 200
        
        # Calculate response size
        response_size = len(response.content) if response.content else 0
        
        # Log performance metrics
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=success,
            request_size=request_size,
            response_size=response_size
        )
        
        # Update legacy metrics for backward compatibility
        mcp.update_metrics(success, response_time)
        
        if success:
            # Handle both JSON and direct image responses
            return handle_generation_response(response)
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            return False, error_msg
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        # Log failed request
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, "Request timed out. The generation is taking too long."
    
    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        # Log failed request
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, "Cannot connect to API server. Please check if the server is running."
    
    except Exception as e:
        response_time = time.time() - start_time
        # Log failed request
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, f"Unexpected error: {str(e)}"

def make_direct_image_request(mcp, request_data: Dict[str, Any], image_index: int = 0) -> Tuple[bool, Any]:
    """Make API request for direct image generation that returns actual image data"""
    
    start_time = time.time()
    
    try:
        # Calculate request size
        request_size = len(json.dumps(request_data).encode('utf-8'))
        
        # Use longer timeout for multiple image generation
        is_multiple_generation = "sequential_image_generation_options" in request_data
        timeout_duration = 300 if is_multiple_generation else 120  # 5 minutes for multiple, 2 minutes for single
        
        # Add image_index as query parameter
        params = {'image_index': image_index}
        
        response = requests.post(
            mcp.endpoints['byteplus_generate_image'],
            json=request_data,
            params=params,
            timeout=timeout_duration
        )
        
        response_time = time.time() - start_time
        success = response.status_code == 200
        
        # Calculate response size
        response_size = len(response.content) if response.content else 0
        
        # Log performance metrics
        log_api_performance(
            endpoint='byteplus_generate_image',
            response_time=response_time,
            success=success,
            request_size=request_size,
            response_size=response_size
        )
        
        # Update legacy metrics for backward compatibility
        mcp.update_metrics(success, response_time)
        
        if success:
            # For direct image response, convert to base64 for display
            image_data = response.content
            content_type = response.headers.get('content-type', 'image/png')
            image_b64 = base64.b64encode(image_data).decode()
            
            # Get metadata from headers
            total_images = int(response.headers.get('X-Total-Images', '1'))
            current_index = int(response.headers.get('X-Image-Index', '0'))
            
            # Create a standardized response format compatible with existing display code
            result = {
                'data': [{
                    'b64_json': image_b64,
                    'metadata': {
                        'format': content_type,
                        'size': len(image_data),
                        'index': current_index,
                        'total': total_images,
                        'response_type': 'direct_image'
                    }
                }]
            }
            return True, result
        else:
            error_msg = f"API Error {response.status_code}: {response.text}"
            return False, error_msg
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        log_api_performance(
            endpoint='byteplus_generate_image',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, "Request timed out. The generation is taking too long."
    
    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        log_api_performance(
            endpoint='byteplus_generate_image',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, "Cannot connect to API server. Please check if the server is running."
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_performance(
            endpoint='byteplus_generate_image',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, f"Unexpected error: {str(e)}"

def handle_generation_response(response) -> Tuple[bool, Any]:
    """Handle both JSON and direct image responses from BytePlus API"""
    
    try:
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            # Standard JSON response
            result = response.json()
            return True, result
        
        elif 'image/' in content_type:
            # Direct image response - convert to base64
            image_data = response.content
            image_b64 = base64.b64encode(image_data).decode()
            
            # Create a standardized response format
            result = {
                'images': [f"data:{content_type};base64,{image_b64}"],
                'metadata': {
                    'format': content_type,
                    'size': len(image_data),
                    'response_type': 'direct_image'
                }
            }
            return True, result
        
        else:
            # Try to parse as JSON first, fallback to treating as image
            try:
                result = response.json()
                return True, result
            except:
                # Assume it's image data
                image_data = response.content
                image_b64 = base64.b64encode(image_data).decode()
                
                result = {
                    'images': [f"data:image/png;base64,{image_b64}"],
                    'metadata': {
                        'format': 'image/png',
                        'size': len(image_data),
                        'response_type': 'assumed_image'
                    }
                }
                return True, result
                 
    except Exception as e:
        return False, f"Error processing response: {str(e)}"
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        # Log failed request
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, "Request timed out. The generation is taking too long."
    
    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        # Log failed request
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, "Cannot connect to API server. Please check if the server is running."
    
    except Exception as e:
        response_time = time.time() - start_time
        # Log failed request
        log_api_performance(
            endpoint='byteplus_generate',
            response_time=response_time,
            success=False
        )
        mcp.update_metrics(False, response_time)
        return False, f"Unexpected error: {str(e)}"

def display_generation_results(result: Dict[str, Any]):
    """Display generated images and metadata using responsive layout"""
    
    if not result:
        st.warning("No results to display")
        return
    
    # Extract images from result
    images = []
    if 'images' in result:
        images = result['images']
    elif 'image_urls' in result:
        images = result['image_urls']
    elif 'data' in result and isinstance(result['data'], list):
        images = result['data']
    
    if not images:
        st.warning("No images found in the result")
        st.json(result)  # Show raw result for debugging
        return
    
    st.markdown("### 🖼️ Generated Images")
    
    # Prepare image data for responsive grid
    image_grid_data = []
    for idx, image_data in enumerate(images):
        grid_item = {
            'caption': f"Image {idx + 1}",
            'metadata': {
                'Index': idx + 1,
                'Format': 'PNG',
                'Generated': datetime.now().strftime('%H:%M:%S')
            }
        }
        
        try:
            # Handle different image data formats
            if isinstance(image_data, dict):
                # Dictionary format (e.g., {"url": "...", "size": "..."})
                if 'url' in image_data:
                    grid_item['url'] = image_data['url']
                    grid_item['image'] = image_data['url']
                    # Add size information if available
                    if 'size' in image_data:
                        grid_item['metadata']['Size'] = image_data['size']
                elif 'image' in image_data:
                    # Handle base64 in dictionary format
                    image_str = image_data['image']
                    if image_str.startswith('data:image'):
                        header, data = image_str.split(',', 1)
                        image_bytes = base64.b64decode(data)
                        image = Image.open(io.BytesIO(image_bytes))
                        grid_item['image'] = image
                        grid_item['base64'] = data
                    else:
                        grid_item['url'] = image_str
                        grid_item['image'] = image_str
            elif isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    # Base64 encoded image
                    header, data = image_data.split(',', 1)
                    image_bytes = base64.b64decode(data)
                    image = Image.open(io.BytesIO(image_bytes))
                    grid_item['image'] = image
                    grid_item['base64'] = data
                elif image_data.startswith('http'):
                    # URL
                    grid_item['url'] = image_data
                    grid_item['image'] = image_data
                else:
                    # Assume base64 without header
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    grid_item['image'] = image
                    grid_item['base64'] = image_data
            
            image_grid_data.append(grid_item)
            
        except Exception as e:
            st.error(f"Error processing image {idx + 1}: {str(e)}")
    
    # Use responsive image grid
    render_responsive_image_grid(image_grid_data, max_cols=3)
    
    # Download section
    st.markdown("### 📥 Download Options")
    download_cols = ResponsiveLayout.create_responsive_columns("downloads", min_cols=2, max_cols=4)
    
    for idx, grid_item in enumerate(image_grid_data):
        with download_cols[idx % len(download_cols)]:
            if 'url' in grid_item:
                st.markdown(f"[📥 Download Image {idx + 1}]({grid_item['url']})")
            elif 'base64' in grid_item:
                st.download_button(
                    label=f"📥 Download Image {idx + 1}",
                    data=base64.b64decode(grid_item['base64']),
                    file_name=f"generated_image_{idx + 1}_{int(time.time())}.png",
                    mime="image/png",
                    key=f"download_{idx}_{int(time.time())}"
                )
    
    # Show generation metadata
    st.subheader("📋 Generation Details")
    st.json(result)

def update_generation_stats(success: bool, num_images: int):
    """Update generation statistics"""
    if 'generation_stats' not in st.session_state:
        st.session_state.generation_stats = {
            'total_images': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'success_rate': 0.0
        }
    
    stats = st.session_state.generation_stats
    
    if success:
        stats['successful_generations'] += 1
        stats['total_images'] += num_images
    else:
        stats['failed_generations'] += 1
    
    total_generations = stats['successful_generations'] + stats['failed_generations']
    if total_generations > 0:
        stats['success_rate'] = (stats['successful_generations'] / total_generations) * 100
    
    st.session_state.generation_stats = stats