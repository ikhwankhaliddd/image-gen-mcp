# BytePlus Image Generation MCP - Streamlit Frontend

## Overview

This Streamlit-based frontend provides an intuitive user interface for the BytePlus Image Generation Model Control Panel (MCP). It offers comprehensive controls for image generation, real-time monitoring, and performance analytics.

## Features

### 🎨 BytePlus Generation Interface
- **Text-to-Image Generation**: Single and multiple image generation from text prompts
- **Image-to-Image Generation**: Transform existing images with reference images
- **Image Expansion**: Expand single images to multiple variations
- **Interactive Controls**: Intuitive sliders, dropdowns, and input fields
- **Real-time Preview**: Live image display with download capabilities

### 📊 Performance Dashboard
- **Real-time Metrics**: CPU, memory, and system resource monitoring
- **API Performance**: Response times, throughput, and success rates
- **Performance Alerts**: Automatic warnings for system issues
- **Historical Data**: Trends and analytics over time
- **Export Capabilities**: Download metrics as CSV

### 🎯 Advanced Features
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Comprehensive error management and user feedback
- **Progress Tracking**: Real-time generation progress indicators
- **Image Comparison**: Side-by-side, slider, and grid comparisons
- **Notification System**: User-friendly alerts and status updates

## Getting Started

### Prerequisites

1. **Python Environment**: Python 3.8 or higher
2. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

3. **Backend Server**: Ensure the FastAPI backend is running
   ```bash
   python main.py
   ```

### Running the Application

1. **Start Streamlit**:
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

2. **Access the Interface**:
   - Local URL: http://localhost:8501
   - Network URL: http://[your-ip]:8501

## Interface Guide

### Navigation

The application features a sidebar navigation with the following sections:

- **🎨 BytePlus Generation**: Main image generation interface
- **🎭 Style Planning**: Style and aesthetic planning tools
- **👤 Character Generation**: Character-specific generation features
- **📊 Performance Dashboard**: System monitoring and analytics
- **🚨 Error Dashboard**: Error tracking and management

### BytePlus Generation Page

#### Generation Types

1. **Text2Img (Single)**
   - Generate a single image from text prompt
   - Adjustable image size and style parameters

2. **Text2Img (Multiple)**
   - Generate multiple images from text prompt
   - Batch processing with customizable count

3. **Img2Img (Single Reference)**
   - Transform image using single reference
   - Upload base image and reference image

4. **Img2Img (Multiple Reference)**
   - Transform image using multiple references
   - Upload base image and multiple reference images

5. **Img2Img (Expand to Multiple)**
   - Expand single image to multiple variations
   - Generate diverse outputs from one input

#### Controls

- **Prompt Input**: Text description for image generation
- **Image Size**: Dropdown selection (512x512, 768x768, 1024x1024)
- **Number of Images**: Slider for batch generation (1-10)
- **Style Selection**: Predefined style options
- **Advanced Settings**: Additional parameters and fine-tuning

#### Image Upload

- **Drag & Drop**: Intuitive file upload interface
- **Format Support**: PNG, JPG, JPEG formats
- **Preview**: Immediate image preview after upload
- **Validation**: Automatic file format and size checking

### Performance Dashboard

#### Overview Metrics

- **Total Requests**: Cumulative API calls
- **Success Rate**: Percentage of successful operations
- **Average Response Time**: Mean API response duration
- **Throughput**: Requests per minute

#### System Monitoring

- **CPU Usage**: Real-time processor utilization
- **Memory Usage**: RAM consumption tracking
- **Performance Charts**: Historical trends and patterns
- **Alert System**: Automatic warnings for resource issues

#### Detailed Analytics

- **API Call History**: Detailed request logs
- **Response Time Trends**: Performance over time
- **Error Rate Analysis**: Failure pattern identification
- **Export Options**: CSV download for external analysis

## Configuration

### API Endpoints

The application connects to the following backend endpoints:

```python
endpoints = {
    'byteplus_generate': 'http://localhost:8003/byteplus-generate',
    'generate': 'http://localhost:8003/generate',
    'plan': 'http://localhost:8003/plan',
    'generate_chara': 'http://localhost:8003/generate-chara'
}
```

### Customization

#### Styling

Custom CSS is applied for enhanced visual appeal:
- Modern color scheme with gradients
- Responsive layout design
- Interactive hover effects
- Professional typography

#### Performance Settings

- **Metrics History**: Configurable retention (default: 1000 entries)
- **Monitoring Interval**: System metrics collection frequency
- **Alert Thresholds**: Customizable warning levels

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify backend server is running on port 8003
   - Check network connectivity
   - Ensure firewall settings allow connections

2. **Performance Issues**
   - Monitor system resources in Performance Dashboard
   - Check for high CPU/memory usage
   - Review error logs in Error Dashboard

3. **Image Upload Problems**
   - Verify file format (PNG, JPG, JPEG)
   - Check file size limitations
   - Ensure proper file permissions

### Error Handling

The application includes comprehensive error handling:
- **User-friendly Messages**: Clear error descriptions
- **Suggested Solutions**: Actionable troubleshooting steps
- **Error Logging**: Detailed logs for debugging
- **Graceful Degradation**: Fallback interfaces when components fail

## API Integration

### Request Format

The frontend sends requests to the backend in the following format:

```json
{
    "generation_type": "text2img_single",
    "prompt": "A beautiful landscape",
    "image_size": "1024x1024",
    "num_images": 1,
    "style": "realistic",
    "advanced_settings": {
        "guidance_scale": 7.5,
        "num_inference_steps": 50
    }
}
```

### Response Handling

Responses are processed and displayed with:
- **Image Rendering**: Base64 decoded images
- **Error Management**: Status code and message handling
- **Progress Updates**: Real-time generation status
- **Download Options**: Individual image downloads

## Performance Optimization

### Best Practices

1. **Batch Processing**: Use multiple image generation for efficiency
2. **Resource Monitoring**: Regular performance dashboard checks
3. **Error Prevention**: Input validation and user guidance
4. **Cache Management**: Automatic cleanup of temporary data

### Monitoring

- **Real-time Metrics**: Continuous system monitoring
- **Historical Analysis**: Trend identification and optimization
- **Alert System**: Proactive issue detection
- **Export Capabilities**: Data analysis and reporting

## Support

For technical support or feature requests:
1. Check the Error Dashboard for system issues
2. Review Performance Dashboard for resource problems
3. Examine detailed logs in the application
4. Refer to backend API documentation for endpoint details

## Version Information

- **Streamlit Version**: 1.28.0+
- **Python Version**: 3.8+
- **Backend Compatibility**: FastAPI-based BytePlus MCP
- **Browser Support**: Modern browsers with JavaScript enabled