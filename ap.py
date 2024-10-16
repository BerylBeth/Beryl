import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np

# Create the Dash app
app = dash.Dash(__name__)

# Task list and platform ratings
tasks = [
    'Generating local data', 'Writing funding proposals', 'Analyzing economic data',
    'Creating data visualizations', 'Writing reports', 'Conducting action research',
    'Making presentations', 'Summarizing technical reports', 'Creating a PowerPoint from a report',
    'Creating a dashboard to track project progress'
]

ratings = {
    'ChatGPT': [4, 5, 3, 2, 5, 3, 4, 4, 3, 1],
    'Perplexity': [5, 2, 5, 1, 3, 4, 2, 5, 1, 3],
    'Claude': [3, 4, 4, 3, 4, 5, 3, 5, 4, 5],
    'Bard': [4, 3, 4, 2, 5, 3, 4, 4, 2, 4]  # Added Bard's ratings
}

# Color scheme with Bard added
colors = {
    'background': '#F0F8FF',
    'text': '#1E3D59',
    'ChatGPT': '#FF6B6B',
    'Perplexity': '#4ECDC4',
    'Claude': '#FFA500',
    'Bard': '#9ACD32'  # Distinctive green color for Bard
}

# Define the layout of the app
app.layout = html.Div([
    html.H1("AI Platform Comparison for Economic Development Tasks",
            style={'textAlign': 'center', 'color': colors['text'], 'marginBottom': 30}),
    
    html.Div([
        html.H3("Instructions:", style={'color': colors['text']}),
        html.Ul([
            html.Li("Use the sliders below to set the importance of each task (1 = least important, 5 = most important)."),
            html.Li("Scroll down to view the charts, which will update automatically based on your inputs. The bar chart shows the overall ranking of platforms based on your importance ratings."),
            html.Li("View the radar chart (below the bar chart) to compare platforms across all tasks."),
            html.Li("Use the refresh button on your browser to reset the importance values.")
        ], style={'color': colors['text']})
    ], style={'marginBottom': 30}),
    
    # Create sliders for each task
    html.Div([
        html.Div([
            html.Label(f"{task} importance:", style={'fontWeight': 'bold', 'color': colors['text']}),
            dcc.Slider(
                id=f'slider-{i}',
                min=1,
                max=5,
                step=1,
                value=1,  # Default slider value set to 1
                marks={i: str(i) for i in range(1, 6)},
                included=True
            )
        ], style={'marginBottom': 20}) for i, task in enumerate(tasks)
    ], id="sliders-container"),
    
    # Placeholder for the bar chart
    dcc.Graph(id='bar-chart'),
    
    # Placeholder for the radar chart
    dcc.Graph(id='radar-chart')
])

# Callback to update sliders and charts
@app.callback(
    [Output(f'slider-{i}', 'value') for i in range(len(tasks))] +
    [Output('bar-chart', 'figure'), Output('radar-chart', 'figure')],
    [Input(f'slider-{i}', 'value') for i in range(len(tasks))]
)
def update_charts(*slider_values):
    slider_values = list(slider_values)

    # Apply milder exponential weighting to the sliders for differentiation
    weights = [w ** 1.5 for w in slider_values]

    # Calculate weighted scores with a softer penalty/boost system and add 0.1 to avoid zeros
    weighted_scores = {
        platform: [
            (w * (r + 0.1)) * (1.1 if r > 3 else 0.9)  # Apply softer penalty and ensure non-zero values
            for w, r in zip(weights, ratings[platform])
        ]
        for platform in ratings
    }
    
    # Calculate total weighted scores and normalize them
    total_scores = {
        platform: sum(weighted_scores[platform])
        for platform in ratings
    }
    max_score = max(total_scores.values())
    min_score = min(total_scores.values())
    
    # Normalize the scores to enhance differentiation but avoid zeros
    normalized_scores = {
        platform: (total_scores[platform] - min_score) / (max_score - min_score) * 100
        for platform in total_scores
    }
    
    # Sort platforms by their total scores
    sorted_platforms = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
    platforms = [item[0] for item in sorted_platforms]
    scores = [item[1] for item in sorted_platforms]
    
    # Create bar chart
    bar_fig = go.Figure(data=[
        go.Bar(x=platforms, y=scores, 
               marker_color=[colors[platform] for platform in platforms],
               text=[f"{score:.1f}" for score in scores],
               textposition='auto')
    ])
    bar_fig.update_layout(
        title="AI Platform Ranking Based on Task Importance",
        xaxis_title="Platforms",
        yaxis_title="Overall Score",
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    # Create radar chart
    radar_fig = go.Figure()
    for platform in ratings:
        radar_fig.add_trace(go.Scatterpolar(
            r=ratings[platform],
            theta=tasks,
            fill='toself',
            name=platform,
            line_color=colors[platform]
        ))
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=True,
        title="Platform Comparison Across Tasks",
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    
    return tuple(slider_values) + (bar_fig, radar_fig)

# Run the app
if __name__ == '__main__':
    server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
