"""
BytePlus Image Generation MCP - Streamlit Frontend
==================================================

A comprehensive Streamlit-based frontend interface for the BytePlus Image Generation
Model Control Panel (MCP) that provides an intuitive user experience for all
image generation capabilities.

Features:
- Interactive controls for model configuration
- Real-time visualization of outputs
- Responsive design
- Error handling and user feedback
- Performance monitoring
"""

import streamlit as st
import requests
import json
import time
from typing import Dict, List, Optional, Any
from PIL import Image
import io
import base64
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.responsive_layout import (
    ErrorHandler, render_error_dashboard, render_notification_system,
    render_responsive_metrics, add_notification
)
from components.performance_metrics import (
    render_performance_overview, render_system_metrics, render_api_performance_charts,
    render_detailed_metrics_table, render_performance_alerts, render_performance_recommendations,
    start_performance_monitoring, log_api_performance
)
from components.byteplus_interface import render_byteplus_generation_interface


# Page configuration
st.set_page_config(
    page_title="BytePlus Image Generation MCP",
    page_icon="assets/app_icon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
    
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #e3f2fd;
        color: #0d47a1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generation_history' not in st.session_state:
    st.session_state.generation_history = []
if 'api_metrics' not in st.session_state:
    st.session_state.api_metrics = {
        'total_requests': 0,
        'successful_requests': 0,
        'failed_requests': 0,
        'avg_response_time': 0,
        'response_times': []
    }

class MCPInterface:
    """Main MCP Interface class for managing the Streamlit application"""
    
    def __init__(self):
        self.api_base_url = "http://69.5.1.247/svc3"
        self.endpoints = {
            'byteplus_generate': f"{self.api_base_url}/byteplus-generate",
            'byteplus_generate_image': f"{self.api_base_url}/byteplus-generate-image",
            'generate': f"{self.api_base_url}/generate",
            'plan': f"{self.api_base_url}/plan",
            'generate_chara': f"{self.api_base_url}/generate-chara"
        }
        start_performance_monitoring()
    
    def render_header(self):
        """Render the main application header"""
        # Center the logo and title using columns
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.image(image="assets/byteplus.png", use_column_width=True)
            st.markdown('''
            <div class="main-header" style="text-align: center;">
                BytePlus Image Generation MCP
            </div>
            ''', 
                    unsafe_allow_html=True)
        
        st.markdown("---")
    
    def render_sidebar(self):
        """Render the sidebar navigation and configuration"""
        with st.sidebar:
            st.markdown("### 🚀 Navigation")
            
            # Main navigation
            page = st.selectbox(
                "Select Feature",
                ["BytePlus Generation", "Style Planning", "Character Generation", "Performance Dashboard", "Error Dashboard"],
                key="main_navigation"
            )
            
            st.markdown("---")
            
            # API Configuration
            st.markdown("### ⚙️ Configuration")
            
            # Server status check
            server_status = self.check_server_status()
            if server_status:
                st.success("✅ Server Online")
            else:
                st.error("❌ Server Offline")
            
            # API endpoint configuration
            with st.expander("API Settings"):
                new_base_url = st.text_input(
                    "API Base URL", 
                    value=self.api_base_url,
                    help="Base URL for the API server"
                )
                if new_base_url != self.api_base_url:
                    self.api_base_url = new_base_url
                    self.update_endpoints()
                
                st.info("💡 Make sure your API server is running on the specified URL")
            
            # Quick metrics
            st.markdown("### 📊 Quick Stats")
            metrics = st.session_state.api_metrics
            st.metric("Total Requests", metrics['total_requests'])
            st.metric("Success Rate", 
                     f"{(metrics['successful_requests'] / max(metrics['total_requests'], 1) * 100):.1f}%")
            
            return page
    
    def check_server_status(self) -> bool:
        """Check if the API server is running"""
        try:
            response = requests.get(f"{self.api_base_url}/docs", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def update_endpoints(self):
        """Update API endpoints when base URL changes"""
        self.endpoints = {
            'byteplus_generate': f"{self.api_base_url}/byteplus-generate",
            'generate': f"{self.api_base_url}/generate",
            'plan': f"{self.api_base_url}/plan",
            'generate_chara': f"{self.api_base_url}/generate-chara"
        }
    
    def update_metrics(self, success: bool, response_time: float):
        """Update API call metrics"""
        metrics = st.session_state.api_metrics
        metrics['total_requests'] += 1
        if success:
            metrics['successful_requests'] += 1
        else:
            metrics['failed_requests'] += 1
        
        metrics['response_times'].append(response_time)
        metrics['avg_response_time'] = sum(metrics['response_times']) / len(metrics['response_times'])
        
        # Keep only last 100 response times for performance
        if len(metrics['response_times']) > 100:
            metrics['response_times'] = metrics['response_times'][-100:]

def main():
    """Main application function"""
    
    # Initialize error handler
    error_handler = ErrorHandler()
    
    # Initialize MCP interface
    mcp = MCPInterface()
    
    # Render notifications
    render_notification_system()
    
    # Render header
    mcp.render_header()
    
    # Render sidebar and get selected page
    selected_page = mcp.render_sidebar()
    
    # Render main content based on selected page with error handling
    try:
        if selected_page == "BytePlus Generation":
            render_byteplus_generation_page(mcp)
        elif selected_page == "Style Planning":
            render_style_planning_page(mcp)
        elif selected_page == "Character Generation":
            render_character_generation_page(mcp)
        elif selected_page == "Performance Dashboard":
            render_performance_dashboard(mcp)
        elif selected_page == "Error Dashboard":
            render_error_dashboard()
    except Exception as e:
        error_handler.handle_error(e, f"Rendering {selected_page} page")
        st.error("An error occurred while loading the page. Please try refreshing or check the Error Dashboard for details.")

def render_byteplus_generation_page(mcp: MCPInterface):
    """Render the BytePlus image generation page"""
    st.markdown('<div class="section-header">BytePlus Image Generation</div>', 
               unsafe_allow_html=True)
    
    # Import and render the BytePlus interface
    try:
        render_byteplus_generation_interface(mcp)
    except ImportError:
        st.error("❌ BytePlus interface component not found. Please check the components directory.")
    except Exception as e:
        error_msg = str(e) if e is not None else "Unknown error occurred"
        st.error(f"❌ Error loading BytePlus interface: {error_msg}")
        
        # Fallback interface
        st.info("🚧 Using fallback interface")
        with st.expander("📋 Available Use Cases", expanded=True):
            st.markdown("""
            **Supported Generation Types:**
            1. **Text2Img (Single)** - Generate one image from text prompt
            2. **Text2Img (Multiple)** - Generate multiple coherent images
            3. **Img2Img (Single Reference)** - Transform reference image
            4. **Img2Img (Multiple References)** - Use multiple reference images
            5. **Img2Img (Expand to Multiple)** - Create variations from one image
            """)

def render_style_planning_page(mcp: MCPInterface):
    """Render the style planning page"""
    st.markdown('<div class="section-header">Style Planning</div>', 
               unsafe_allow_html=True)
    st.info("🚧 Style Planning interface coming soon")

def render_character_generation_page(mcp: MCPInterface):
    """Render the character generation page"""
    st.markdown('<div class="section-header">Character Generation</div>', 
               unsafe_allow_html=True)
    st.info("🚧 Character Generation interface coming soon")

def render_performance_dashboard(mcp: MCPInterface):
    """Render comprehensive performance dashboard"""
    st.markdown("## 📊 Performance Dashboard")
    
    # Performance overview with key metrics
    render_performance_overview()
    
    st.markdown("---")
    
    # System metrics
    render_system_metrics()
    
    st.markdown("---")
    
    # API performance charts
    render_api_performance_charts()
    
    st.markdown("---")
    
    # Performance alerts
    render_performance_alerts()
    
    st.markdown("---")
    
    # Performance recommendations
    render_performance_recommendations()
    
    st.markdown("---")
    
    # Detailed metrics table
    render_detailed_metrics_table()

if __name__ == "__main__":
    main()