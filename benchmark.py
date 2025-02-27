import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Define data directory
DATA_DIR = 'data'

# Read the CSV files
llama3_very_long = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama3:latest-very-long.csv'))
llama3_long = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama3:latest-long.csv'))
llama3_short = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama3:latest-short.csv'))

llama2_very_long = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama2:7b-chat-q4_K_M-very-long.csv'))
llama2_long = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama2:7b-chat-q4_K_M-long.csv'))
llama2_short = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama2:7b-chat-q4_K_M-short.csv'))

llama3_8b_very_long = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama3:8b-instruct-q2_K-very-long.csv'))
llama3_8b_long = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama3:8b-instruct-q2_K-long.csv'))
llama3_8b_short = pd.read_csv(os.path.join(DATA_DIR, 'ADA6000-Latest', 'llama3:8b-instruct-q2_K-short.csv'))

models = {
    'Llama 3': {'very_long': llama3_very_long, 'long': llama3_long, 'short': llama3_short},
    'Llama 2 7B': {'very_long': llama2_very_long, 'long': llama2_long, 'short': llama2_short},
    'Llama 3 8B': {'very_long': llama3_8b_very_long, 'long': llama3_8b_long, 'short': llama3_8b_short}
}

colors = {'Llama 3': '#1f77b4', 'Llama 2 7B': '#ff7f0e', 'Llama 3 8B': '#2ca02c'}

def convert_size_to_gb(size_str):
    """Convert size string (e.g., '3.6T', '198G') to GB as float"""
    size_str = str(size_str)
    multipliers = {'T': 1024, 'G': 1, 'M': 1/1024}
    number = float(size_str[:-1])
    unit = size_str[-1]
    return number * multipliers[unit]

def create_performance_plots(data_type='long'):
    # 1. GPU Performance Metrics
    fig_gpu = make_subplots(
        rows=2, cols=2,
        subplot_titles=('GPU Utilization (%)', 'Power Draw (W)', 
                       'Clock Speed (MHz)', 'Fan Speed (%)'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 2. Memory Metrics
    fig_memory = make_subplots(
        rows=2, cols=2,
        subplot_titles=('GPU Memory Used (MB)', 'GPU Memory Utilization (%)',
                       'System RAM Used (MB)', 'System RAM Utilization (%)'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # 3. System Metrics
    fig_system = make_subplots(
        rows=2, cols=2,
        subplot_titles=('CPU Usage (%)', 'GPU Temperature (°C)',
                       'Disk Used (GB)', 'Disk Usage (%)'),
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )

    # Add traces for each model
    for model_name, data in models.items():
        # GPU Performance Metrics
        fig_gpu.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['utilization_gpu'],
                                    name=model_name, line=dict(color=colors[model_name])), row=1, col=1)
        fig_gpu.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['power_draw'],
                                    name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=1, col=2)
        fig_gpu.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['clocks_sm'],
                                    name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=1)
        fig_gpu.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['fan_speed'],
                                    name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=2)

        # Memory Metrics
        fig_memory.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['gpu_mem_used'],
                                       name=model_name, line=dict(color=colors[model_name])), row=1, col=1)
        fig_memory.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['utilization_mem'],
                                       name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=1, col=2)
        fig_memory.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['ram_used'],
                                       name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=1)
        ram_util = data[data_type]['ram_used'] / data[data_type]['ram_total'] * 100
        fig_memory.add_trace(go.Scatter(x=data[data_type].index, y=ram_util,
                                       name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=2)

        # System Metrics
        fig_system.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['cpu_usage'],
                                       name=model_name, line=dict(color=colors[model_name])), row=1, col=1)
        fig_system.add_trace(go.Scatter(x=data[data_type].index, y=data[data_type]['gpu_temp'],
                                       name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=1, col=2)
        
        # Convert disk values to GB before calculations
        disk_used_gb = data[data_type]['disk_used'].apply(convert_size_to_gb)
        disk_total_gb = data[data_type]['disk_total'].apply(convert_size_to_gb)
        
        fig_system.add_trace(go.Scatter(x=data[data_type].index, y=disk_used_gb,
                                       name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=1)
        disk_util = (disk_used_gb / disk_total_gb) * 100
        fig_system.add_trace(go.Scatter(x=data[data_type].index, y=disk_util,
                                       name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=2)

    # Update axis labels
    for fig in [fig_gpu, fig_memory, fig_system]:
        for row in [1, 2]:
            for col in [1, 2]:
                fig.update_xaxes(title_text="Time (seconds)", row=row, col=col)

    # Add hardware context to titles
    hardware_context = "NVIDIA RTX 6000 Ada (48GB GDDR6)"
    test_type = "Long Response" if data_type == 'long' else "Short Response"

    layout_updates = dict(
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
            font=dict(size=10)
        ),
        width=1200,
        height=800,
        margin=dict(t=100, r=150)
    )

    fig_gpu.update_layout(
        title_text=f"GPU Performance Metrics - {test_type}<br><sup>{hardware_context}</sup>",
        title_x=0.5,
        title_y=0.95,
        title_xanchor='center',
        title_yanchor='top',
        **layout_updates
    )

    fig_memory.update_layout(
        title_text=f"Memory Usage Metrics - {test_type}<br><sup>{hardware_context}</sup>",
        title_x=0.5,
        title_y=0.95,
        title_xanchor='center',
        title_yanchor='top',
        **layout_updates
    )

    fig_system.update_layout(
        title_text=f"System Metrics - {test_type}<br><sup>{hardware_context}</sup>",
        title_x=0.5,
        title_y=0.95,
        title_xanchor='center',
        title_yanchor='top',
        **layout_updates
    )

    return fig_gpu, fig_memory, fig_system

# Create one large figure with all subplots
fig = make_subplots(
    rows=9, cols=2,  # Increased to 9 rows to accommodate very long tests
    subplot_titles=(
        # Very Long Response Metrics
        'GPU Utilization (%) - Very Long', 'Power Draw (W) - Very Long',
        'Memory Usage (MB) - Very Long', 'Memory Utilization (%) - Very Long',
        'CPU Usage (%) - Very Long', 'Temperature (°C) - Very Long',
        # Long Response Metrics
        'GPU Utilization (%) - Long', 'Power Draw (W) - Long',
        'Memory Usage (MB) - Long', 'Memory Utilization (%) - Long',
        'CPU Usage (%) - Long', 'Temperature (°C) - Long',
        # Short Response Metrics
        'GPU Utilization (%) - Short', 'Power Draw (W) - Short',
        'Memory Usage (MB) - Short', 'Memory Utilization (%) - Short',
        'CPU Usage (%) - Short', 'Temperature (°C) - Short'
    ),
    vertical_spacing=0.03,  # Reduced spacing to fit all plots
    horizontal_spacing=0.1
)

# Add traces for each model
for model_name, data in models.items():
    # Very Long Response - Top Third
    fig.add_trace(go.Scatter(x=data['very_long'].index, y=data['very_long']['utilization_gpu'],
                            name=model_name, line=dict(color=colors[model_name])), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['very_long'].index, y=data['very_long']['power_draw'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=1, col=2)
    fig.add_trace(go.Scatter(x=data['very_long'].index, y=data['very_long']['gpu_mem_used'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=1)
    fig.add_trace(go.Scatter(x=data['very_long'].index, y=data['very_long']['utilization_mem'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=2, col=2)
    fig.add_trace(go.Scatter(x=data['very_long'].index, y=data['very_long']['cpu_usage'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=3, col=1)
    fig.add_trace(go.Scatter(x=data['very_long'].index, y=data['very_long']['gpu_temp'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=3, col=2)

    # Long Response - Middle Third
    # GPU & Power
    fig.add_trace(go.Scatter(x=data['long'].index, y=data['long']['utilization_gpu'],
                            name=model_name, line=dict(color=colors[model_name])), row=4, col=1)
    fig.add_trace(go.Scatter(x=data['long'].index, y=data['long']['power_draw'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=4, col=2)
    
    # Memory
    fig.add_trace(go.Scatter(x=data['long'].index, y=data['long']['gpu_mem_used'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=5, col=1)
    fig.add_trace(go.Scatter(x=data['long'].index, y=data['long']['utilization_mem'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=5, col=2)
    
    # CPU & Temperature
    fig.add_trace(go.Scatter(x=data['long'].index, y=data['long']['cpu_usage'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=6, col=1)
    fig.add_trace(go.Scatter(x=data['long'].index, y=data['long']['gpu_temp'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=6, col=2)

    # Short Response - Bottom Third
    # GPU & Power
    fig.add_trace(go.Scatter(x=data['short'].index, y=data['short']['utilization_gpu'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=7, col=1)
    fig.add_trace(go.Scatter(x=data['short'].index, y=data['short']['power_draw'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=7, col=2)
    
    # Memory
    fig.add_trace(go.Scatter(x=data['short'].index, y=data['short']['gpu_mem_used'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=8, col=1)
    fig.add_trace(go.Scatter(x=data['short'].index, y=data['short']['utilization_mem'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=8, col=2)
    
    # CPU & Temperature
    fig.add_trace(go.Scatter(x=data['short'].index, y=data['short']['cpu_usage'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=9, col=1)
    fig.add_trace(go.Scatter(x=data['short'].index, y=data['short']['gpu_temp'],
                            name=model_name, line=dict(color=colors[model_name]), showlegend=False), row=9, col=2)

# Update layout
fig.update_layout(
    title_text="LLM Performance Metrics - NVIDIA RTX 6000 Ada (48GB GDDR6)",
    title_x=0.5,
    title_y=0.99,
    title_xanchor='center',
    title_yanchor='top',
    showlegend=True,
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.02,
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.2)",
        borderwidth=1,
        font=dict(size=10)
    ),
    height=3000,  # Increased height for additional plots
    width=1200,
    margin=dict(t=100, r=150)
)

# Update x-axis labels
for i in range(1, 10):  # Updated range to include all 9 rows
    for j in range(1, 3):
        fig.update_xaxes(title_text="Time (seconds)", row=i, col=j)

# Add section headers using annotations
fig.add_annotation(
    text="Very Long Response Tests",
    xref="paper", yref="paper",
    x=0, y=0.90,
    xanchor="left",
    showarrow=False,
    font=dict(size=16, color="black"),
    bgcolor="rgba(255, 255, 255, 0.8)"
)

fig.add_annotation(
    text="Long Response Tests",
    xref="paper", yref="paper",
    x=0, y=0.57,
    xanchor="left",
    showarrow=False,
    font=dict(size=16, color="black"),
    bgcolor="rgba(255, 255, 255, 0.8)"
)

fig.add_annotation(
    text="Short Response Tests",
    xref="paper", yref="paper",
    x=0, y=0.24,
    xanchor="left",
    showarrow=False,
    font=dict(size=16, color="black"),
    bgcolor="rgba(255, 255, 255, 0.8)"
)

# Show the figure
fig.show()

# Create summary statistics table
def create_summary_stats():
    stats_data = []
    
    for model_name, data in models.items():
        for test_type in ['very_long', 'long', 'short']:
            df = data[test_type]
            
            # Convert metrics to numeric values for better sorting
            stats = {
                'Model': model_name,
                'Test Type': test_type.replace('_', ' ').title(),
                'Peak GPU Utilization (%)': round(df['utilization_gpu'].max(), 1),
                'Avg GPU Utilization (%)': round(df['utilization_gpu'].mean(), 1),
                'Peak Power Draw (W)': round(df['power_draw'].max(), 1),
                'Avg Power Draw (W)': round(df['power_draw'].mean(), 1),
                'Peak VRAM Used (GB)': round(df['gpu_mem_used'].max() / 1024, 1),
                'Avg VRAM Used (GB)': round(df['gpu_mem_used'].mean() / 1024, 1),
                'Peak Temperature (°C)': round(df['gpu_temp'].max(), 1),
                'Avg Temperature (°C)': round(df['gpu_temp'].mean(), 1),
                'Peak CPU Usage (%)': round(df['cpu_usage'].max(), 1),
                'Avg CPU Usage (%)': round(df['cpu_usage'].mean(), 1),
                'Test Duration (s)': round(len(df) * 0.2, 1),
                'Memory Efficiency (%)': round((df['gpu_mem_used'].mean() / df['gpu_mem_total'].mean() * 100), 1)
            }
            stats_data.append(stats)
    
    stats_df = pd.DataFrame(stats_data)
    
    # Create table figure
    fig_table = go.Figure(data=[go.Table(
        header=dict(
            values=list(stats_df.columns),
            fill_color='lightgrey',
            align='left',
            font=dict(size=12),
            height=40
        ),
        cells=dict(
            values=[stats_df[col] for col in stats_df.columns],
            fill_color=[['white', 'lightblue'] * (len(stats_df)//2)],
            align='left',
            font=dict(size=11),
            height=30
        ),
        columnwidth=[2, 1.5] + [1] * (len(stats_df.columns)-2),  # Wider columns for Model and Test Type
        columnorder=list(range(len(stats_df.columns))),
        customdata=stats_df.values,  # Add data for sorting
    )])
    
    # Add sorting buttons
    buttons = []
    for i, col in enumerate(stats_df.columns):
        buttons.append(
            dict(
                args=[{"cells": {"values": [stats_df.sort_values(col)[c] for c in stats_df.columns]}}],
                label=f"Sort by {col}",
                method="restyle"
            )
        )
        buttons.append(
            dict(
                args=[{"cells": {"values": [stats_df.sort_values(col, ascending=False)[c] for c in stats_df.columns]}}],
                label=f"Sort by {col} (desc)",
                method="restyle"
            )
        )

    # Update layout with sorting buttons
    fig_table.update_layout(
        title_text="Performance Summary Statistics - NVIDIA RTX 6000 Ada (48GB GDDR6)<br><sup>Click column headers to sort</sup>",
        title_x=0.5,
        title_y=0.95,
        width=1500,
        height=400,
        margin=dict(t=80, b=20, l=20, r=20),
        updatemenus=[
            dict(
                buttons=buttons,
                direction="down",
                showactive=True,
                x=1.02,
                xanchor="left",
                y=0.8,
                yanchor="top",
                bgcolor='white',
                font=dict(size=10)
            )
        ]
    )
    
    return fig_table

# Create and display the summary table
fig_table = create_summary_stats()
fig_table.show()