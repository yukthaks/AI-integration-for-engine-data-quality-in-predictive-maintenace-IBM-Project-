import os
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import random
import requests
import datetime

SERVER_API_URL = "http://localhost:5000/predict"

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

historical_data = {key: [] for key in ["Engine rpm", "Lub oil pressure", "Fuel pressure", "Coolant pressure", "lub oil temp", "Coolant temp"]}
time_stamps = []

def generate_live_data():
    """Simulate live engine sensor data."""
    return {
        "Engine rpm": round(random.uniform(600, 3000), 2),
        "Lub oil pressure": round(random.uniform(10, 100), 2),
        "Fuel pressure": round(random.uniform(30, 100), 2),
        "Coolant pressure": round(random.uniform(20, 60), 2),
        "lub oil temp": round(random.uniform(70, 120), 2),
        "Coolant temp": round(random.uniform(60, 100), 2)
    }

app.layout = dbc.Container([
    dbc.Row([dbc.Col(html.H1("Engine Data Dashboard"), width=12)], className="mt-4"),
    
    dbc.Row([dbc.Col(dcc.Graph(id="live-chart"), width=12)], className="mt-4"),
    
    dbc.Row([dbc.Col(dcc.Graph(id="time-series-chart"), width=12)], className="mt-4"),
    
    dbc.Row([dbc.Col(html.Div(id="prediction-div", style={"fontSize": "20px", "marginTop": "20px"}), width=12)]),

    dbc.Row([
        dbc.Col(dash_table.DataTable(
            id="sensor-table",
            columns=[{"name": col, "id": col} for col in ["Time"] + list(historical_data.keys())],
            style_table={'overflowX': 'auto'}
        ), width=12)
    ], className="mt-4"),
    
    dcc.Interval(id="interval-component", interval=5000, n_intervals=0)  
], fluid=True)

@app.callback(
    [Output("live-chart", "figure"),
     Output("time-series-chart", "figure"),
     Output("prediction-div", "children"),
     Output("sensor-table", "data")],
    Input("interval-component", "n_intervals")
)
def update_dashboard(n):
    live_data = generate_live_data()
    
    time_stamps.append(datetime.datetime.now().strftime("%H:%M:%S"))
    for key in live_data.keys():
        historical_data[key].append(live_data[key])

    bar_fig = go.Figure(data=[
        go.Bar(name=key, x=[key], y=[value]) for key, value in live_data.items()
    ])
    bar_fig.update_layout(barmode='group', title='Live Engine Sensor Data')

    line_fig = go.Figure()
    for key in historical_data.keys():
        line_fig.add_trace(go.Scatter(x=time_stamps, y=historical_data[key], mode='lines+markers', name=key))
    line_fig.update_layout(title="Sensor Data Over Time", xaxis_title="Time", yaxis_title="Value")

    warnings = []
    if live_data["Coolant temp"] > 90:
        warnings.append("High Coolant Temperature!")
    if live_data["Lub oil pressure"] < 20:
        warnings.append("Low Lub Oil Pressure!")
    if live_data["Fuel pressure"] < 40:
        warnings.append("Low Fuel Pressure!")
    
    alert_message = " | ".join(warnings) if warnings else "All sensors normal"

    payload = {
        "input_data": [
            {
                "fields": list(live_data.keys()),
                "values": [list(live_data.values())]
            }
        ]
    }
    
    try:
        response = requests.post(SERVER_API_URL, json=payload)
        if response.status_code == 200:
            prediction = response.json()
            prediction_text = f"{alert_message} | Prediction: {prediction['prediction']} ({prediction['confidence']}% confidence)"

        else:
            prediction_text = f"Prediction Error: {response.text}"
    except Exception as e:
        prediction_text = f"Error calling prediction server: {str(e)}"

    table_data = [{"Time": time_stamps[i], **{key: historical_data[key][i] for key in historical_data}} for i in range(len(time_stamps))]

    return bar_fig, line_fig, html.Div(prediction_text), table_data

if __name__ == "__main__":
    app.run_server(debug=True)
