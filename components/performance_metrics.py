"""
Performance Metrics and Monitoring Components
============================================

Advanced performance monitoring, metrics collection, and visualization
components for the BytePlus Image Generation MCP.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from collections import deque
import threading
import queue

class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.initialize_metrics()
    
    def initialize_metrics(self):
        """Initialize performance metrics in session state"""
        
        if 'performance_metrics' not in st.session_state:
            st.session_state.performance_metrics = {
                'api_calls': deque(maxlen=self.max_history),
                'response_times': deque(maxlen=self.max_history),
                'system_metrics': deque(maxlen=self.max_history),
                'error_rates': deque(maxlen=self.max_history),
                'throughput': deque(maxlen=self.max_history),
                'memory_usage': deque(maxlen=self.max_history),
                'cpu_usage': deque(maxlen=self.max_history),
                'generation_stats': {
                    'total_images': 0,
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'avg_generation_time': 0.0,
                    'peak_memory': 0.0,
                    'peak_cpu': 0.0
                }
            }
    
    def record_api_call(self, endpoint: str, response_time: float, success: bool, 
                       request_size: int = 0, response_size: int = 0):
        """Record API call metrics"""
        
        metrics = st.session_state.performance_metrics
        timestamp = datetime.now()
        
        # Record API call
        call_data = {
            'timestamp': timestamp,
            'endpoint': endpoint,
            'response_time': response_time,
            'success': success,
            'request_size': request_size,
            'response_size': response_size
        }
        
        metrics['api_calls'].append(call_data)
        metrics['response_times'].append(response_time)
        
        # Update generation stats
        stats = metrics['generation_stats']
        stats['total_requests'] += 1
        
        if success:
            stats['successful_requests'] += 1
        else:
            stats['failed_requests'] += 1
        
        # Update average generation time
        if len(metrics['response_times']) > 0:
            stats['avg_generation_time'] = sum(metrics['response_times']) / len(metrics['response_times'])
    
    def record_system_metrics(self):
        """Record current system metrics"""
        
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            
            timestamp = datetime.now()
            
            system_data = {
                'timestamp': timestamp,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': memory_used_gb,
                'memory_available_gb': memory.available / (1024**3)
            }
            
            metrics = st.session_state.performance_metrics
            metrics['system_metrics'].append(system_data)
            metrics['cpu_usage'].append(cpu_percent)
            metrics['memory_usage'].append(memory_percent)
            
            # Update peak values
            stats = metrics['generation_stats']
            stats['peak_cpu'] = max(stats['peak_cpu'], cpu_percent)
            stats['peak_memory'] = max(stats['peak_memory'], memory_percent)
            
        except Exception as e:
            st.error(f"Error recording system metrics: {e}")
    
    def calculate_throughput(self, time_window_minutes: int = 5):
        """Calculate API throughput for the given time window"""
        
        metrics = st.session_state.performance_metrics
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=time_window_minutes)
        
        recent_calls = [
            call for call in metrics['api_calls']
            if call['timestamp'] >= cutoff_time
        ]
        
        throughput = len(recent_calls) / time_window_minutes  # calls per minute
        metrics['throughput'].append(throughput)
        
        return throughput
    
    def calculate_error_rate(self, time_window_minutes: int = 5):
        """Calculate error rate for the given time window"""
        
        metrics = st.session_state.performance_metrics
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(minutes=time_window_minutes)
        
        recent_calls = [
            call for call in metrics['api_calls']
            if call['timestamp'] >= cutoff_time
        ]
        
        if not recent_calls:
            error_rate = 0.0
        else:
            failed_calls = sum(1 for call in recent_calls if not call['success'])
            error_rate = (failed_calls / len(recent_calls)) * 100
        
        metrics['error_rates'].append(error_rate)
        return error_rate

def render_performance_overview():
    """Render performance overview with key metrics"""
    
    st.markdown("### 📊 Performance Overview")
    
    monitor = PerformanceMonitor()
    monitor.record_system_metrics()
    
    metrics = st.session_state.performance_metrics
    stats = metrics['generation_stats']
    
    # Key performance indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Requests",
            stats['total_requests'],
            delta=None,
            help="Total number of API requests made"
        )
    
    with col2:
        success_rate = (stats['successful_requests'] / max(stats['total_requests'], 1)) * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta=None,
            help="Percentage of successful API requests"
        )
    
    with col3:
        st.metric(
            "Avg Response Time",
            f"{stats['avg_generation_time']:.2f}s",
            delta=None,
            help="Average API response time"
        )
    
    with col4:
        current_throughput = monitor.calculate_throughput(5)
        st.metric(
            "Throughput (5min)",
            f"{current_throughput:.1f}/min",
            delta=None,
            help="API calls per minute in the last 5 minutes"
        )

def render_system_metrics():
    """Render real-time system metrics"""
    
    st.markdown("### 🖥️ System Metrics")
    
    metrics = st.session_state.performance_metrics
    
    if not metrics['system_metrics']:
        st.info("No system metrics available yet. Metrics will appear as the system is used.")
        return
    
    # Current system status
    latest_metrics = metrics['system_metrics'][-1]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cpu_color = "normal"
        if latest_metrics['cpu_percent'] > 80:
            cpu_color = "inverse"
        elif latest_metrics['cpu_percent'] > 60:
            cpu_color = "off"
        
        st.metric(
            "CPU Usage",
            f"{latest_metrics['cpu_percent']:.1f}%",
            help="Current CPU utilization"
        )
    
    with col2:
        memory_color = "normal"
        if latest_metrics['memory_percent'] > 80:
            memory_color = "inverse"
        elif latest_metrics['memory_percent'] > 60:
            memory_color = "off"
        
        st.metric(
            "Memory Usage",
            f"{latest_metrics['memory_percent']:.1f}%",
            help="Current memory utilization"
        )
    
    with col3:
        st.metric(
            "Memory Used",
            f"{latest_metrics['memory_used_gb']:.2f} GB",
            help="Current memory usage in GB"
        )
    
    # System metrics charts
    if len(metrics['system_metrics']) > 1:
        render_system_charts(metrics)

def render_system_charts(metrics: Dict):
    """Render system performance charts"""
    
    # Prepare data for charts
    timestamps = [m['timestamp'] for m in metrics['system_metrics']]
    cpu_data = [m['cpu_percent'] for m in metrics['system_metrics']]
    memory_data = [m['memory_percent'] for m in metrics['system_metrics']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CPU Usage Chart
        fig_cpu = go.Figure()
        fig_cpu.add_trace(go.Scatter(
            x=timestamps,
            y=cpu_data,
            mode='lines+markers',
            name='CPU Usage',
            line=dict(color='#ff6b6b', width=2),
            fill='tonexty'
        ))
        
        fig_cpu.update_layout(
            title="CPU Usage Over Time",
            xaxis_title="Time",
            yaxis_title="CPU Usage (%)",
            yaxis=dict(range=[0, 100]),
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig_cpu, use_container_width=True)
    
    with col2:
        # Memory Usage Chart
        fig_memory = go.Figure()
        fig_memory.add_trace(go.Scatter(
            x=timestamps,
            y=memory_data,
            mode='lines+markers',
            name='Memory Usage',
            line=dict(color='#4ecdc4', width=2),
            fill='tonexty'
        ))
        
        fig_memory.update_layout(
            title="Memory Usage Over Time",
            xaxis_title="Time",
            yaxis_title="Memory Usage (%)",
            yaxis=dict(range=[0, 100]),
            height=300,
            showlegend=False
        )
        
        st.plotly_chart(fig_memory, use_container_width=True)

def render_api_performance_charts():
    """Render API performance charts"""
    
    st.markdown("### 📈 API Performance")
    
    metrics = st.session_state.performance_metrics
    
    if not metrics['api_calls']:
        st.info("No API performance data available yet. Data will appear after making API calls.")
        return
    
    # Response time chart
    if len(metrics['response_times']) > 1:
        timestamps = [call['timestamp'] for call in metrics['api_calls']]
        response_times = list(metrics['response_times'])
        
        fig_response = go.Figure()
        fig_response.add_trace(go.Scatter(
            x=timestamps,
            y=response_times,
            mode='lines+markers',
            name='Response Time',
            line=dict(color='#45b7d1', width=2)
        ))
        
        fig_response.update_layout(
            title="API Response Times",
            xaxis_title="Time",
            yaxis_title="Response Time (seconds)",
            height=400
        )
        
        st.plotly_chart(fig_response, use_container_width=True)
    
    # Throughput and error rate charts
    col1, col2 = st.columns(2)
    
    with col1:
        if len(metrics['throughput']) > 1:
            fig_throughput = go.Figure()
            fig_throughput.add_trace(go.Scatter(
                y=list(metrics['throughput']),
                mode='lines+markers',
                name='Throughput',
                line=dict(color='#96ceb4', width=2)
            ))
            
            fig_throughput.update_layout(
                title="API Throughput (calls/min)",
                yaxis_title="Calls per Minute",
                height=300
            )
            
            st.plotly_chart(fig_throughput, use_container_width=True)
    
    with col2:
        if len(metrics['error_rates']) > 1:
            fig_errors = go.Figure()
            fig_errors.add_trace(go.Scatter(
                y=list(metrics['error_rates']),
                mode='lines+markers',
                name='Error Rate',
                line=dict(color='#ff6b6b', width=2)
            ))
            
            fig_errors.update_layout(
                title="Error Rate (%)",
                yaxis_title="Error Rate (%)",
                yaxis=dict(range=[0, 100]),
                height=300
            )
            
            st.plotly_chart(fig_errors, use_container_width=True)

def render_detailed_metrics_table():
    """Render detailed metrics in table format"""
    
    st.markdown("### 📋 Detailed Metrics")
    
    metrics = st.session_state.performance_metrics
    
    if not metrics['api_calls']:
        st.info("No detailed metrics available yet.")
        return
    
    # Convert API calls to DataFrame
    api_data = []
    for call in list(metrics['api_calls'])[-50:]:  # Last 50 calls
        api_data.append({
            'Timestamp': call['timestamp'].strftime('%H:%M:%S'),
            'Endpoint': call['endpoint'],
            'Response Time (s)': f"{call['response_time']:.2f}",
            'Status': '✅ Success' if call['success'] else '❌ Failed',
            'Request Size (KB)': f"{call.get('request_size', 0) / 1024:.1f}",
            'Response Size (KB)': f"{call.get('response_size', 0) / 1024:.1f}"
        })
    
    if api_data:
        df = pd.DataFrame(api_data)
        st.dataframe(df, use_container_width=True)
    
    # Export functionality
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Metrics to CSV"):
            csv_data = pd.DataFrame(api_data).to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🗑️ Clear Metrics History"):
            # Clear metrics but keep structure
            for key in ['api_calls', 'response_times', 'system_metrics', 'error_rates', 'throughput']:
                metrics[key].clear()
            
            # Reset stats
            metrics['generation_stats'] = {
                'total_images': 0,
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_generation_time': 0.0,
                'peak_memory': 0.0,
                'peak_cpu': 0.0
            }
            
            st.success("Metrics history cleared!")
            st.rerun()

def render_performance_alerts():
    """Render performance alerts and warnings"""
    
    st.markdown("### ⚠️ Performance Alerts")
    
    metrics = st.session_state.performance_metrics
    alerts = []
    
    # Check for performance issues
    if metrics['system_metrics']:
        latest_system = metrics['system_metrics'][-1]
        
        if latest_system['cpu_percent'] > 90:
            alerts.append({
                'type': 'error',
                'message': f"🔥 High CPU usage: {latest_system['cpu_percent']:.1f}%"
            })
        elif latest_system['cpu_percent'] > 70:
            alerts.append({
                'type': 'warning',
                'message': f"⚠️ Elevated CPU usage: {latest_system['cpu_percent']:.1f}%"
            })
        
        if latest_system['memory_percent'] > 90:
            alerts.append({
                'type': 'error',
                'message': f"🔥 High memory usage: {latest_system['memory_percent']:.1f}%"
            })
        elif latest_system['memory_percent'] > 70:
            alerts.append({
                'type': 'warning',
                'message': f"⚠️ Elevated memory usage: {latest_system['memory_percent']:.1f}%"
            })
    
    # Check API performance
    if len(metrics['response_times']) > 5:
        recent_avg = sum(list(metrics['response_times'])[-5:]) / 5
        if recent_avg > 10:
            alerts.append({
                'type': 'error',
                'message': f"🐌 Slow API responses: {recent_avg:.2f}s average"
            })
        elif recent_avg > 5:
            alerts.append({
                'type': 'warning',
                'message': f"⏱️ Slower API responses: {recent_avg:.2f}s average"
            })
    
    # Check error rates
    if len(metrics['error_rates']) > 0:
        latest_error_rate = metrics['error_rates'][-1]
        if latest_error_rate > 20:
            alerts.append({
                'type': 'error',
                'message': f"🚨 High error rate: {latest_error_rate:.1f}%"
            })
        elif latest_error_rate > 10:
            alerts.append({
                'type': 'warning',
                'message': f"⚠️ Elevated error rate: {latest_error_rate:.1f}%"
            })
    
    # Display alerts
    if alerts:
        for alert in alerts:
            if alert['type'] == 'error':
                st.error(alert['message'])
            elif alert['type'] == 'warning':
                st.warning(alert['message'])
    else:
        st.success("✅ All systems operating normally")

def render_performance_recommendations():
    """Render performance optimization recommendations"""
    
    st.markdown("### 💡 Performance Recommendations")
    
    metrics = st.session_state.performance_metrics
    recommendations = []
    
    # Analyze metrics and generate recommendations
    if metrics['system_metrics']:
        latest_system = metrics['system_metrics'][-1]
        
        if latest_system['cpu_percent'] > 80:
            recommendations.append(
                "🔧 Consider reducing concurrent operations or optimizing CPU-intensive tasks"
            )
        
        if latest_system['memory_percent'] > 80:
            recommendations.append(
                "💾 Consider clearing cache or reducing memory usage by processing smaller batches"
            )
    
    if len(metrics['response_times']) > 10:
        avg_response = sum(metrics['response_times']) / len(metrics['response_times'])
        if avg_response > 5:
            recommendations.append(
                "⚡ API responses are slow. Consider optimizing prompts or reducing image complexity"
            )
    
    stats = metrics['generation_stats']
    if stats['total_requests'] > 0:
        success_rate = (stats['successful_requests'] / stats['total_requests']) * 100
        if success_rate < 90:
            recommendations.append(
                "🎯 Success rate is below 90%. Check API configuration and network connectivity"
            )
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            st.info(rec)
    else:
        st.success("🎉 System is performing optimally!")

# Utility functions for integration
def start_performance_monitoring():
    """Start background performance monitoring"""
    
    monitor = PerformanceMonitor()
    monitor.initialize_metrics()
    
    # Record initial system metrics
    monitor.record_system_metrics()

def log_api_performance(endpoint: str, response_time: float, success: bool, 
                       request_size: int = 0, response_size: int = 0):
    """Log API performance metrics"""
    
    monitor = PerformanceMonitor()
    monitor.record_api_call(endpoint, response_time, success, request_size, response_size)