"""
Responsive Layout and Error Handling Components
===============================================

Components for responsive design that adapts to different screen sizes
and comprehensive error handling with user feedback mechanisms.
"""

import streamlit as st
import traceback
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponsiveLayout:
    """Responsive layout manager for different screen sizes"""
    
    @staticmethod
    def get_screen_size():
        """Detect screen size category based on viewport"""
        # Note: Streamlit doesn't provide direct viewport access,
        # so we use container width as a proxy
        return "desktop"  # Default assumption
    
    @staticmethod
    def get_columns_for_screen(screen_size: str, content_type: str) -> int:
        """Get optimal number of columns based on screen size and content type"""
        
        column_configs = {
            "mobile": {
                "images": 1,
                "metrics": 2,
                "controls": 1,
                "cards": 1
            },
            "tablet": {
                "images": 2,
                "metrics": 3,
                "controls": 2,
                "cards": 2
            },
            "desktop": {
                "images": 3,
                "metrics": 4,
                "controls": 3,
                "cards": 3
            }
        }
        
        return column_configs.get(screen_size, column_configs["desktop"]).get(content_type, 2)
    
    @staticmethod
    def create_responsive_columns(content_type: str, min_cols: int = 1, max_cols: int = 4):
        """Create responsive columns based on content type"""
        screen_size = ResponsiveLayout.get_screen_size()
        num_cols = ResponsiveLayout.get_columns_for_screen(screen_size, content_type)
        num_cols = max(min_cols, min(max_cols, num_cols))
        return st.columns(num_cols)

class ErrorHandler:
    """Comprehensive error handling and user feedback system"""
    
    def __init__(self):
        self.initialize_error_tracking()
    
    def initialize_error_tracking(self):
        """Initialize error tracking in session state"""
        if 'error_history' not in st.session_state:
            st.session_state.error_history = []
        if 'error_notifications' not in st.session_state:
            st.session_state.error_notifications = []
    
    @contextmanager
    def error_boundary(self, operation_name: str, show_traceback: bool = False):
        """Context manager for error handling with user feedback"""
        try:
            yield
        except Exception as e:
            self.handle_error(e, operation_name, show_traceback)
    
    def handle_error(self, error: Exception, operation_name: str, show_traceback: bool = False):
        """Handle and log errors with user-friendly messages"""
        
        error_info = {
            'timestamp': datetime.now(),
            'operation': operation_name,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc() if show_traceback else None
        }
        
        # Log error safely
        safe_operation_name = str(operation_name) if operation_name is not None else "Unknown Operation"
        safe_error = str(error) if error is not None else "Unknown Error"
        logger.error(f"Error in {safe_operation_name}: {safe_error}")
        
        # Store in session state
        st.session_state.error_history.append(error_info)
        
        # Keep only last 50 errors
        if len(st.session_state.error_history) > 50:
            st.session_state.error_history = st.session_state.error_history[-50:]
        
        # Show user-friendly error message
        self.show_error_message(error, operation_name, show_traceback)
    
    def show_error_message(self, error: Exception, operation_name: str, show_traceback: bool = False):
        """Display user-friendly error messages"""
        
        error_messages = {
            'ConnectionError': "🌐 **Connection Error**: Unable to connect to the API server. Please check if the server is running.",
            'TimeoutError': "⏱️ **Timeout Error**: The operation took too long. Please try again or reduce the complexity.",
            'ValueError': "⚠️ **Invalid Input**: Please check your input parameters and try again.",
            'FileNotFoundError': "📁 **File Not Found**: The requested file could not be found.",
            'PermissionError': "🔒 **Permission Error**: Insufficient permissions to perform this operation.",
            'KeyError': "🔑 **Configuration Error**: Missing required configuration. Please check your settings.",
            'requests.exceptions.ConnectionError': "🌐 **API Connection Error**: Cannot reach the API server. Please verify the server is running.",
            'requests.exceptions.Timeout': "⏱️ **API Timeout**: The API request timed out. Please try again.",
            'requests.exceptions.HTTPError': "🚫 **API Error**: The API returned an error. Please check your request.",
        }
        
        error_type = type(error).__name__
        if hasattr(error, '__module__') and error.__module__:
            full_error_type = f"{error.__module__}.{error_type}"
        else:
            full_error_type = error_type
        
        # Get user-friendly message
        user_message = error_messages.get(full_error_type, error_messages.get(error_type))
        
        if user_message:
            st.error(user_message)
        else:
            st.error(f"❌ **Error in {operation_name}**: {str(error)}")
        
        # Show technical details in expander
        with st.expander("🔧 Technical Details", expanded=False):
            st.code(f"Operation: {operation_name}")
            st.code(f"Error Type: {error_type}")
            st.code(f"Error Message: {str(error)}")
            
            if show_traceback:
                st.code(traceback.format_exc())
        
        # Suggest solutions
        self.suggest_solutions(error_type, operation_name)
    
    def suggest_solutions(self, error_type: str, operation_name: str):
        """Suggest solutions based on error type and operation"""
        
        solutions = {
            'ConnectionError': [
                "Check if the API server is running on the correct port",
                "Verify the API base URL in settings",
                "Check your internet connection",
                "Try restarting the API server"
            ],
            'TimeoutError': [
                "Try reducing the image size or complexity",
                "Check your internet connection speed",
                "Increase the timeout setting if available",
                "Try again during off-peak hours"
            ],
            'ValueError': [
                "Check all input fields for valid values",
                "Ensure image files are in supported formats",
                "Verify prompt length is within limits",
                "Check numerical parameters are within valid ranges"
            ],
            'FileNotFoundError': [
                "Ensure the file path is correct",
                "Check file permissions",
                "Verify the file exists and is accessible",
                "Try uploading the file again"
            ]
        }
        
        if error_type in solutions:
            st.info("💡 **Suggested Solutions:**")
            for solution in solutions[error_type]:
                st.markdown(f"• {solution}")

def render_error_dashboard():
    """Render error tracking dashboard"""
    
    st.markdown("### 🚨 Error Dashboard")
    
    error_history = st.session_state.get('error_history', [])
    
    if not error_history:
        st.success("✅ No errors recorded!")
        return
    
    # Error statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Errors", len(error_history))
    
    with col2:
        recent_errors = [e for e in error_history if (datetime.now() - e['timestamp']).seconds < 3600]
        st.metric("Last Hour", len(recent_errors))
    
    with col3:
        error_types = [e['error_type'] for e in error_history]
        most_common = max(set(error_types), key=error_types.count) if error_types else "None"
        st.metric("Most Common", most_common)
    
    with col4:
        if st.button("🗑️ Clear History"):
            st.session_state.error_history = []
            st.rerun()
    
    # Error timeline
    st.markdown("#### Recent Errors")
    
    for error in reversed(error_history[-10:]):  # Show last 10 errors
        with st.expander(
            f"🔴 {error['error_type']} in {error['operation']} - {error['timestamp'].strftime('%H:%M:%S')}",
            expanded=False
        ):
            st.markdown(f"**Operation:** {error['operation']}")
            st.markdown(f"**Error Type:** {error['error_type']}")
            st.markdown(f"**Message:** {error['error_message']}")
            st.markdown(f"**Time:** {error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            if error.get('traceback'):
                st.code(error['traceback'])

def render_loading_states():
    """Render various loading states and progress indicators"""
    
    st.markdown("### ⏳ Loading States")
    
    # Different loading indicators
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Standard Loading")
        with st.spinner("Processing..."):
            st.write("Content loading...")
    
    with col2:
        st.markdown("#### Progress Bar")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate progress (in real app, this would be actual progress)
        import time
        for i in range(100):
            progress_bar.progress(i + 1)
            status_text.text(f'Progress: {i+1}%')
            time.sleep(0.01)

def render_notification_system():
    """Render notification system for user feedback"""
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    notifications = st.session_state.notifications
    
    # Display active notifications
    for idx, notification in enumerate(notifications):
        if notification['type'] == 'success':
            st.success(notification['message'])
        elif notification['type'] == 'error':
            st.error(notification['message'])
        elif notification['type'] == 'warning':
            st.warning(notification['message'])
        elif notification['type'] == 'info':
            st.info(notification['message'])
        
        # Auto-dismiss after showing
        if notification.get('auto_dismiss', True):
            notifications.pop(idx)

def add_notification(message: str, notification_type: str = 'info', auto_dismiss: bool = True):
    """Add a notification to the system"""
    
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
    
    notification = {
        'message': message,
        'type': notification_type,
        'timestamp': datetime.now(),
        'auto_dismiss': auto_dismiss
    }
    
    st.session_state.notifications.append(notification)

def render_responsive_image_grid(images: List[Dict], max_cols: int = 4):
    """Render responsive image grid that adapts to screen size"""
    
    if not images:
        st.info("No images to display")
        return
    
    # Determine number of columns based on screen size
    num_cols = ResponsiveLayout.get_columns_for_screen("desktop", "images")
    num_cols = min(num_cols, max_cols, len(images))
    
    # Calculate rows needed
    rows = (len(images) + num_cols - 1) // num_cols
    
    # Display images in responsive grid
    for row in range(rows):
        cols = st.columns(num_cols)
        for col_idx in range(num_cols):
            img_idx = row * num_cols + col_idx
            if img_idx < len(images) and images[img_idx]:
                with cols[col_idx]:
                    image_data = images[img_idx]
                    
                    # Validate image_data
                    if not isinstance(image_data, dict):
                        st.error(f"Invalid image data at index {img_idx}")
                        continue
                    
                    # Safe caption generation
                    default_caption = f"Image {img_idx + 1}" if img_idx is not None else "Image"
                    caption = image_data.get('caption', default_caption)
                    
                    # Safe image source
                    image_source = image_data.get('image', image_data.get('url'))
                    if not image_source:
                        st.error(f"No image source found for {caption}")
                        continue
                    
                    st.image(
                        image_source,
                        caption=caption,
                        use_column_width=True
                    )
                    
                    # Additional image metadata
                    if 'metadata' in image_data and isinstance(image_data['metadata'], dict):
                        st.caption("ℹ️ Details:")
                        for key, value in image_data['metadata'].items():
                            safe_key = str(key) if key is not None else "Unknown"
                            safe_value = str(value) if value is not None else "N/A"
                            st.caption(f"• {safe_key}: {safe_value}")

def render_responsive_metrics(metrics: Dict[str, Any]):
    """Render metrics in a responsive layout"""
    
    if not metrics:
        st.info("No metrics to display")
        return
    
    # Determine number of columns
    num_cols = ResponsiveLayout.get_columns_for_screen("desktop", "metrics")
    num_cols = min(num_cols, len(metrics))
    
    cols = st.columns(num_cols)
    
    for idx, (key, value) in enumerate(metrics.items()):
        with cols[idx % num_cols]:
            if isinstance(value, dict) and 'value' in value:
                st.metric(
                    key,
                    value['value'],
                    delta=value.get('delta'),
                    help=value.get('help')
                )
            else:
                st.metric(key, value)

def safe_execute(func: Callable, *args, operation_name: str = "Operation", **kwargs):
    """Safely execute a function with error handling"""
    
    error_handler = ErrorHandler()
    
    try:
        result = func(*args, **kwargs)
        return result
    except Exception as e:
        # Handle the error through the error handler
        error_handler.handle_error(e, operation_name)
        # Return a consistent format when an error occurs
        return False, f"Error in {operation_name}: {str(e)}"

def validate_inputs(**inputs) -> Dict[str, List[str]]:
    """Validate user inputs and return validation errors"""
    
    errors = {}
    
    for field_name, value in inputs.items():
        field_errors = []
        
        if field_name == 'prompt' and not value.strip():
            field_errors.append("Prompt cannot be empty")
        elif field_name == 'prompt' and len(value) > 1000:
            field_errors.append("Prompt is too long (max 1000 characters)")
        
        if field_name == 'size' and value not in ['1K', '2K', '4K']:
            field_errors.append("Invalid size selection")
        
        if field_name == 'num_images' and (not isinstance(value, int) or value < 1 or value > 10):
            field_errors.append("Number of images must be between 1 and 10")
        
        if field_errors:
            errors[field_name] = field_errors
    
    return errors

def show_validation_errors(errors: Dict[str, List[str]]):
    """Display validation errors to the user"""
    
    if not errors:
        return
    
    st.error("❌ **Please fix the following errors:**")
    
    for field, field_errors in errors.items():
        st.markdown(f"**{field.title()}:**")
        for error in field_errors:
            st.markdown(f"• {error}")

# Utility decorators for error handling
def with_error_handling(operation_name: str):
    """Decorator for automatic error handling"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            return safe_execute(func, *args, operation_name=operation_name, **kwargs)
        return wrapper
    return decorator