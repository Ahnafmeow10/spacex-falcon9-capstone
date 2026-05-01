# SpaceX Falcon 9 Launch Dashboard
# IBM Data Science Capstone - Plotly Dash App
# Replicates the exact IBM lab version

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ── Load Data ──────────────────────────────────────────────────────────────────
# Uses the IBM-provided spacex_launch_dash.csv
# Download it from:
# https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv
spacex_df = pd.read_csv("spacex_launch_dash.csv",
                        dtype={"class": int})

max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# ── App Layout ─────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "SpaceX Launch Dashboard"

app.layout = html.Div(children=[

    # Title
    html.H1(
        "SpaceX Falcon 9 Launch Records Dashboard",
        style={
            "textAlign": "center",
            "color": "#503D36",
            "font-size": 40
        }
    ),

    # ── TASK 1: Launch Site Dropdown ──────────────────────────────────────────
    dcc.Dropdown(
        id="site-dropdown",
        options=[
            {"label": "All Sites",       "value": "ALL"},
            {"label": "CCAFS LC-40",     "value": "CCAFS LC-40"},
            {"label": "CCAFS SLC-40",    "value": "CCAFS SLC-40"},
            {"label": "KSC LC-39A",      "value": "KSC LC-39A"},
            {"label": "VAFB SLC-4E",     "value": "VAFB SLC-4E"},
        ],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # ── TASK 2: Pie Chart ─────────────────────────────────────────────────────
    html.Div(dcc.Graph(id="success-pie-chart")),

    html.Br(),

    html.P("Payload range (Kg):"),

    # ── TASK 3: Payload Range Slider ──────────────────────────────────────────
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={i: str(i) for i in range(0, 11000, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # ── TASK 4: Scatter Chart ─────────────────────────────────────────────────
    html.Div(dcc.Graph(id="success-payload-scatter-chart")),

])


# ── TASK 2 Callback: Pie Chart ─────────────────────────────────────────────────
@app.callback(
    Output(component_id="success-pie-chart",  component_property="figure"),
    Input(component_id="site-dropdown",        component_property="value")
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        # Total successes per site
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site"
        )
    else:
        # Success vs Failure for selected site
        filtered = spacex_df[spacex_df["Launch Site"] == entered_site]
        site_counts = filtered["class"].value_counts().reset_index()
        site_counts.columns = ["class", "count"]
        site_counts["outcome"] = site_counts["class"].map({1: "Success", 0: "Failure"})
        fig = px.pie(
            site_counts,
            values="count",
            names="outcome",
            title=f"Total Launch Outcomes for site {entered_site}",
            color="outcome",
            color_discrete_map={"Success": "#00cc96", "Failure": "#ef553b"}
        )
    return fig


# ── TASK 4 Callback: Scatter Chart ────────────────────────────────────────────
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown",    component_property="value"),
        Input(component_id="payload-slider",   component_property="value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    # Filter by payload range
    mask = (
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    )
    filtered = spacex_df[mask]

    # Filter by site if needed
    if entered_site != "ALL":
        filtered = filtered[filtered["Launch Site"] == entered_site]

    fig = px.scatter(
        filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=(
            f"Correlation between Payload and Success for "
            f"{'All Sites' if entered_site == 'ALL' else entered_site}"
        ),
        labels={"class": "Launch Outcome (1=Success, 0=Failure)"}
    )
    return fig


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
