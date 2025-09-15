"""
Visualization Components for BytePlus MCP
=========================================

Real-time visualization components for model outputs, performance metrics,
and generation progress tracking.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any, Optional
import numpy as np

class RealTimeVisualizer:
    """Real-time visualization manager for generation progress and metrics"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables for visualization"""
        if 'generation_progress' not in st.session_state:
            st.session_state.generation_progress = []
        if 'live_metrics' not in st.session_state:
            st.session_state.live_metrics = {
                'cpu_usage': [],
                'memory_usage': [],
                'gpu_usage': [],
                'timestamps': []
            }
        if 'generation_queue' not in st.session_state:
            st.session_state.generation_queue = []

def render_generation_progress_tracker():
    """Render real-time generation progress tracker"""
    
    st.markdown("### 🔄 Generation Progress")
    
    # Check if there are active generations
    if 'active_generations' not in st.session_state:
        st.session_state.active_generations = {}
    
    active_gens = st.session_state.active_generations
    
    if not active_gens:
        st.info("No active generations")
        return
    
    # Display progress for each active generation
    for gen_id, gen_info in active_gens.items():
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{gen_info['type']}**")
                st.markdown(f"*{gen_info['prompt'][:50]}...*")
            
            with col2:
                progress = gen_info.get('progress', 0)
                st.progress(progress / 100)
                st.caption(f"{progress}%")
            
            with col3:
                elapsed = time.time() - gen_info['start_time']
                st.metric("Elapsed", f"{elapsed:.1f}s")
            
            # Progress bar with steps
            if 'steps' in gen_info:
                current_step = gen_info.get('current_step', 0)
                total_steps = gen_info['steps']
                
                step_progress = current_step / total_steps if total_steps > 0 else 0
                st.progress(step_progress)
                st.caption(f"Step {current_step}/{total_steps}")

def render_live_metrics_dashboard():
    """Render live system metrics dashboard"""
    
    st.markdown("### 📊 Live System Metrics")
    
    # Simulate real-time metrics (in production, these would come from actual monitoring)
    current_time = datetime.now()
    
    # Update metrics in session state
    if 'last_metric_update' not in st.session_state:
        st.session_state.last_metric_update = current_time
    
    # Update every 5 seconds
    if (current_time - st.session_state.last_metric_update).seconds >= 5:
        update_live_metrics()
        st.session_state.last_metric_update = current_time
    
    # Display current metrics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = st.session_state.live_metrics
    
    with col1:
        cpu_current = metrics['cpu_usage'][-1] if metrics['cpu_usage'] else 0
        st.metric(
            "CPU Usage",
            f"{cpu_current:.1f}%",
            delta=f"{cpu_current - (metrics['cpu_usage'][-2] if len(metrics['cpu_usage']) > 1 else cpu_current):.1f}%"
        )
    
    with col2:
        mem_current = metrics['memory_usage'][-1] if metrics['memory_usage'] else 0
        st.metric(
            "Memory Usage",
            f"{mem_current:.1f}%",
            delta=f"{mem_current - (metrics['memory_usage'][-2] if len(metrics['memory_usage']) > 1 else mem_current):.1f}%"
        )
    
    with col3:
        gpu_current = metrics['gpu_usage'][-1] if metrics['gpu_usage'] else 0
        st.metric(
            "GPU Usage",
            f"{gpu_current:.1f}%",
            delta=f"{gpu_current - (metrics['gpu_usage'][-2] if len(metrics['gpu_usage']) > 1 else gpu_current):.1f}%"
        )
    
    with col4:
        queue_size = len(st.session_state.generation_queue)
        st.metric("Queue Size", queue_size)
    
    # Real-time charts
    if metrics['timestamps']:
        render_metrics_charts(metrics)

def update_live_metrics():
    """Update live metrics with simulated data"""
    metrics = st.session_state.live_metrics
    current_time = datetime.now()
    
    # Simulate realistic metrics
    base_cpu = 30 + 20 * np.sin(time.time() / 10)  # Oscillating CPU usage
    base_mem = 45 + 15 * np.sin(time.time() / 15)  # Oscillating memory usage
    base_gpu = 60 + 30 * np.sin(time.time() / 8)   # Oscillating GPU usage
    
    # Add some noise
    cpu_usage = max(0, min(100, base_cpu + np.random.normal(0, 5)))
    mem_usage = max(0, min(100, base_mem + np.random.normal(0, 3)))
    gpu_usage = max(0, min(100, base_gpu + np.random.normal(0, 8)))
    
    # Append to metrics
    metrics['cpu_usage'].append(cpu_usage)
    metrics['memory_usage'].append(mem_usage)
    metrics['gpu_usage'].append(gpu_usage)
    metrics['timestamps'].append(current_time)
    
    # Keep only last 50 data points
    max_points = 50
    for key in ['cpu_usage', 'memory_usage', 'gpu_usage', 'timestamps']:
        if len(metrics[key]) > max_points:
            metrics[key] = metrics[key][-max_points:]

def render_metrics_charts(metrics: Dict[str, List]):
    """Render real-time metrics charts"""
    
    if not metrics['timestamps']:
        return
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Time': metrics['timestamps'],
        'CPU Usage (%)': metrics['cpu_usage'],
        'Memory Usage (%)': metrics['memory_usage'],
        'GPU Usage (%)': metrics['gpu_usage']
    })
    
    # CPU Usage Chart
    fig_cpu = px.line(
        df, x='Time', y='CPU Usage (%)',
        title='CPU Usage Over Time',
        color_discrete_sequence=['#ff6b6b']
    )
    fig_cpu.update_layout(height=200, showlegend=False)
    fig_cpu.update_xaxis(showticklabels=False)
    
    # Memory Usage Chart
    fig_mem = px.line(
        df, x='Time', y='Memory Usage (%)',
        title='Memory Usage Over Time',
        color_discrete_sequence=['#4ecdc4']
    )
    fig_mem.update_layout(height=200, showlegend=False)
    fig_mem.update_xaxis(showticklabels=False)
    
    # GPU Usage Chart
    fig_gpu = px.line(
        df, x='Time', y='GPU Usage (%)',
        title='GPU Usage Over Time',
        color_discrete_sequence=['#45b7d1']
    )
    fig_gpu.update_layout(height=200, showlegend=False)
    
    # Display charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(fig_cpu, use_container_width=True)
        st.plotly_chart(fig_gpu, use_container_width=True)
    
    with col2:
        st.plotly_chart(fig_mem, use_container_width=True)
        
        # Combined metrics chart
        fig_combined = go.Figure()
        fig_combined.add_trace(go.Scatter(
            x=df['Time'], y=df['CPU Usage (%)'],
            mode='lines', name='CPU', line=dict(color='#ff6b6b')
        ))
        fig_combined.add_trace(go.Scatter(
            x=df['Time'], y=df['Memory Usage (%)'],
            mode='lines', name='Memory', line=dict(color='#4ecdc4')
        ))
        fig_combined.add_trace(go.Scatter(
            x=df['Time'], y=df['GPU Usage (%)'],
            mode='lines', name='GPU', line=dict(color='#45b7d1')
        ))
        
        fig_combined.update_layout(
            title='Combined System Metrics',
            height=200,
            yaxis_title='Usage (%)',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_combined, use_container_width=True)

def render_generation_queue_status():
    """Render generation queue status and management"""
    
    st.markdown("### 📋 Generation Queue")
    
    queue = st.session_state.generation_queue
    
    if not queue:
        st.info("Queue is empty")
        return
    
    # Queue statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Items in Queue", len(queue))
    
    with col2:
        estimated_time = len(queue) * 30  # Assume 30 seconds per generation
        st.metric("Estimated Wait", f"{estimated_time}s")
    
    with col3:
        if st.button("🗑️ Clear Queue"):
            st.session_state.generation_queue = []
            st.rerun()
    
    # Queue items
    st.markdown("#### Queue Items")
    
    for idx, item in enumerate(queue):
        with st.container():
            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
            
            with col1:
                st.markdown(f"**#{idx + 1}**")
            
            with col2:
                st.markdown(f"**{item['type']}**")
                st.caption(f"{item['prompt'][:40]}...")
            
            with col3:
                st.caption(f"Added: {item['timestamp'].strftime('%H:%M:%S')}")
                st.caption(f"Size: {item.get('size', 'N/A')}")
            
            with col4:
                if st.button("❌", key=f"remove_{idx}"):
                    st.session_state.generation_queue.pop(idx)
                    st.rerun()

def render_image_comparison_viewer():
    """Render image comparison viewer for before/after or multiple variations"""
    
    st.markdown("### 🔍 Image Comparison")
    
    if 'comparison_images' not in st.session_state:
        st.session_state.comparison_images = []
    
    images = st.session_state.comparison_images
    
    if not images:
        st.info("No images to compare. Generate some images first!")
        return
    
    # Comparison mode selection
    comparison_mode = st.selectbox(
        "Comparison Mode",
        ["Side by Side", "Before/After Slider", "Grid View"],
        key="image_comparison_mode",
        help="Choose how to display images for comparison"
    )
    
    if comparison_mode == "Side by Side":
        render_side_by_side_comparison(images)
    elif comparison_mode == "Before/After Slider":
        render_slider_comparison(images)
    else:
        render_grid_comparison(images)

def render_side_by_side_comparison(images: List[Dict]):
    """Render side-by-side image comparison"""
    
    # Validate images data
    if not images or len(images) < 2:
        st.warning("Need at least 2 images for comparison")
        return
    
    # Filter out None or invalid images
    valid_images = [img for img in images if img and isinstance(img, dict) and 'image' in img and 'prompt' in img]
    
    if len(valid_images) < 2:
        st.warning("Need at least 2 valid images for comparison")
        return
    
    # Image selection
    col1, col2 = st.columns(2)
    
    with col1:
        img1_idx = st.selectbox("Select first image", range(len(valid_images)), format_func=lambda x: f"Image {x+1}", key="comparison_img1_selector")
    
    with col2:
        img2_idx = st.selectbox("Select second image", range(len(valid_images)), format_func=lambda x: f"Image {x+1}", key="comparison_img2_selector")
    
    # Display selected images
    col1, col2 = st.columns(2)
    
    with col1:
        if img1_idx < len(valid_images) and valid_images[img1_idx]:
            st.image(valid_images[img1_idx]['image'], caption=f"Image {img1_idx + 1}", use_column_width=True)
            prompt = valid_images[img1_idx].get('prompt', 'No prompt available')
            st.caption(f"Prompt: {prompt[:50]}..." if prompt else "No prompt available")
    
    with col2:
        if img2_idx < len(valid_images) and valid_images[img2_idx]:
            st.image(valid_images[img2_idx]['image'], caption=f"Image {img2_idx + 1}", use_column_width=True)
            prompt = valid_images[img2_idx].get('prompt', 'No prompt available')
            st.caption(f"Prompt: {prompt[:50]}..." if prompt else "No prompt available")

def render_slider_comparison(images: List[Dict]):
    """Render before/after slider comparison"""
    
    if len(images) < 2:
        st.warning("Need at least 2 images for slider comparison")
        return
    
    st.info("🚧 Slider comparison feature coming soon!")

def render_grid_comparison(images: List[Dict]):
    """Render grid view comparison"""
    
    # Validate images data
    if not images:
        st.warning("No images available for grid comparison")
        return
    
    # Filter out None or invalid images
    valid_images = [img for img in images if img and isinstance(img, dict) and 'image' in img and 'prompt' in img]
    
    if not valid_images:
        st.warning("No valid images available for grid comparison")
        return
    
    # Grid size selection
    cols_per_row = st.slider("Images per row", 2, 4, 3)
    
    # Display images in grid
    rows = (len(valid_images) + cols_per_row - 1) // cols_per_row
    
    for row in range(rows):
        cols = st.columns(cols_per_row)
        for col_idx in range(cols_per_row):
            img_idx = row * cols_per_row + col_idx
            if img_idx < len(valid_images) and valid_images[img_idx]:
                with cols[col_idx]:
                    st.image(valid_images[img_idx]['image'], caption=f"Image {img_idx + 1}", use_column_width=True)
                    prompt = valid_images[img_idx].get('prompt', 'No prompt available')
                    st.caption(f"{prompt[:30]}..." if prompt else "No prompt available")

def add_generation_to_queue(generation_type: str, prompt: str, settings: Dict[str, Any]):
    """Add a generation request to the queue"""
    
    queue_item = {
        'type': generation_type,
        'prompt': prompt,
        'settings': settings,
        'timestamp': datetime.now(),
        'id': f"gen_{int(time.time() * 1000)}"
    }
    
    st.session_state.generation_queue.append(queue_item)

def start_generation_tracking(gen_id: str, generation_type: str, prompt: str, steps: int = 50):
    """Start tracking a generation process"""
    
    if 'active_generations' not in st.session_state:
        st.session_state.active_generations = {}
    
    st.session_state.active_generations[gen_id] = {
        'type': generation_type,
        'prompt': prompt,
        'start_time': time.time(),
        'progress': 0,
        'steps': steps,
        'current_step': 0
    }

def update_generation_progress(gen_id: str, progress: int, current_step: int = None):
    """Update generation progress"""
    
    if gen_id in st.session_state.active_generations:
        st.session_state.active_generations[gen_id]['progress'] = progress
        if current_step is not None:
            st.session_state.active_generations[gen_id]['current_step'] = current_step

def complete_generation(gen_id: str):
    """Mark generation as complete and remove from active tracking"""
    
    if gen_id in st.session_state.active_generations:
        del st.session_state.active_generations[gen_id]