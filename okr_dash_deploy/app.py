import json
from datetime import date
import dash
from dash import Dash, html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# ---------- Dummy Data (Objectives & KRs only) ----------
DATA = {
    "period": "2025-12",
    "objectives": [
        {
            "id": "OBJ-1",
            "title": "Increase Revenue",
            "description": "Enhance sales strategies, optimize marketing, expand reach.",
            "owner": "Liam O'Connor",
            "status": "At Risk",
            "progress_pct": 62,
            "krs": ["KR-1","KR-2","KR-3","KR-4","KR-5","KR-6"]
        },
        {
            "id": "OBJ-2",
            "title": "Customer Satisfaction",
            "description": "Streamline support, improve quality, gather feedback.",
            "owner": "Fatima Masood",
            "status": "Off Track",
            "progress_pct": 41,
            "krs": []
        },
        {
            "id": "OBJ-3",
            "title": "Market Reach",
            "description": "Boost brand visibility and customer growth.",
            "owner": "Jamal Habib",
            "status": "On Track",
            "progress_pct": 78,
            "krs": []
        },
    ],
    "key_results": [
        {
            "id":"KR-1","objective_id":"OBJ-1","title":"Monthly Revenue Growth ($)",
            "unit":"$","owner":"Liam O'Connor","status":"On Track",
            "target":30000,"current":38000,"delta_to_target_pct":30,
            "series":[
                {"period":"2025-01","value":24000,"target":30000},
                {"period":"2025-02","value":26000,"target":30000},
                {"period":"2025-03","value":25000,"target":30000},
                {"period":"2025-04","value":27000,"target":30000},
                {"period":"2025-05","value":31000,"target":30000},
                {"period":"2025-06","value":29000,"target":30000},
                {"period":"2025-07","value":33000,"target":30000},
                {"period":"2025-08","value":34000,"target":30000},
                {"period":"2025-09","value":36000,"target":30000},
                {"period":"2025-10","value":32000,"target":30000},
                {"period":"2025-11","value":35000,"target":30000},
                {"period":"2025-12","value":38000,"target":30000},
            ],
            "notes":[{"date":"2025-12-10","text":"Q4 promos outperformed forecast (+8%)."}]
        },
        {
            "id":"KR-2","objective_id":"OBJ-1","title":"New Customer Acquisition (Qty)",
            "unit":"qty","owner":"Fatima Masood","status":"Off Track",
            "target":371,"current":285,"delta_to_target_pct":-20,
            "series":[
                {"period":"2025-07","value":310,"target":371},
                {"period":"2025-08","value":298,"target":371},
                {"period":"2025-09","value":281,"target":371},
                {"period":"2025-10","value":290,"target":371},
                {"period":"2025-11","value":300,"target":371},
                {"period":"2025-12","value":285,"target":371},
            ],
            "notes":[{"date":"2025-12-05","text":"Paid channel CPC up 18% MoM."}]
        },
        {
            "id":"KR-3","objective_id":"OBJ-1","title":"Upsell Revenue ($)",
            "unit":"$","owner":"Jamal Habib","status":"At Risk",
            "target":9000,"current":7000,"delta_to_target_pct":-20,
            "series":[
                {"period":"2025-07","value":6500,"target":9000},
                {"period":"2025-08","value":7000,"target":9000},
                {"period":"2025-09","value":7200,"target":9000},
                {"period":"2025-10","value":6800,"target":9000},
                {"period":"2025-11","value":7100,"target":9000},
                {"period":"2025-12","value":7000,"target":9000},
            ],
            "notes":[{"date":"2025-12-12","text":"Playbook v2 rollout slipped two weeks."}]
        },
        {
            "id":"KR-4","objective_id":"OBJ-1","title":"Customer Retention Rate (%)",
            "unit":"%","owner":"Ariya Patel","status":"Off Track",
            "target":61,"current":56,"delta_to_target_pct":-6,
            "series":[
                {"period":"2025-07","value":59,"target":61},
                {"period":"2025-08","value":58,"target":61},
                {"period":"2025-09","value":57,"target":61},
                {"period":"2025-10","value":56,"target":61},
                {"period":"2025-11","value":56,"target":61},
                {"period":"2025-12","value":56,"target":61},
            ],
            "notes":[{"date":"2025-12-03","text":"New billing issue increased churn risk."}]
        },
        {
            "id":"KR-5","objective_id":"OBJ-1","title":"Revenue from New Markets ($)",
            "unit":"$","owner":"Michael Brown","status":"On Track",
            "target":24000,"current":39000,"delta_to_target_pct":70,
            "series":[
                {"period":"2025-07","value":20000,"target":24000},
                {"period":"2025-08","value":22000,"target":24000},
                {"period":"2025-09","value":25000,"target":24000},
                {"period":"2025-10","value":28000,"target":24000},
                {"period":"2025-11","value":32000,"target":24000},
                {"period":"2025-12","value":39000,"target":24000},
            ],
            "notes":[{"date":"2025-12-08","text":"MEA distributor onboarded."}]
        },
        {
            "id":"KR-6","objective_id":"OBJ-1","title":"Subscription Renewal Rate (%)",
            "unit":"%","owner":"Olive Brown","status":"On Track",
            "target":50,"current":56,"delta_to_target_pct":6,
            "series":[
                {"period":"2025-07","value":49,"target":50},
                {"period":"2025-08","value":50,"target":50},
                {"period":"2025-09","value":52,"target":50},
                {"period":"2025-10","value":53,"target":50},
                {"period":"2025-11","value":55,"target":50},
                {"period":"2025-12","value":56,"target":50},
            ],
            "notes":[{"date":"2025-12-01","text":"New reminder cadence live."}]
        },
    ]
}

STAT_COLORS = {"On Track":"#10B981", "At Risk":"#F59E0B", "Off Track":"#EF4444", "Default":"#64748B"}

def objective_card(obj, active_id):
    selected = obj["id"] == active_id
    border = "border-success" if selected else "border-0"
    ring = dbc.Progress(value=obj["progress_pct"], striped=False, color="primary", style={"height":"6px"})
    status_dot = html.Span(style={
        "display":"inline-block","width":"10px","height":"10px","borderRadius":"50%",
        "backgroundColor":STAT_COLORS.get(obj["status"], STAT_COLORS["Default"]),
        "marginRight":"6px"
    })
    return dbc.Card(
        dbc.CardBody([
            html.Div([status_dot, html.Small(obj["status"])]),
            html.H6(obj["title"], className="mt-1 mb-1"),
            html.P(obj["description"], className="text-muted mb-2", style={"minHeight":"44px"}),
            ring
        ]),
        id={"type":"objective-card","id":obj["id"]},
        className=f"shadow-sm {border} objective-card",
        style={"cursor":"pointer","minWidth":"260px"}
    )

def kr_mini_chart(kr):
    x = [p["period"] for p in kr["series"]]
    y = [p["value"] for p in kr["series"]]
    target = kr["series"][-1]["target"] if kr["series"] else kr["target"]
    fig = go.Figure()
    fig.add_bar(x=x, y=y, name="Actual")
    fig.add_hline(y=target, line_dash="dash", annotation_text="Target", annotation_position="top right")
    fig.update_layout(
        showlegend=False, margin=dict(l=0,r=0,t=0,b=0),
        height=120, yaxis_title=None, xaxis_title=None,
        xaxis=dict(tickfont=dict(size=10)), yaxis=dict(tickfont=dict(size=10))
    )
    if y:
        colors = ["#94A3B8"]*(len(y)-1)+[STAT_COLORS.get(kr["status"], STAT_COLORS["Default"])]
        fig.data[0].marker.update(color=colors)
    return fig

def kr_card(kr):
    status = kr["status"]
    color = STAT_COLORS.get(status, STAT_COLORS["Default"])
    current = kr["current"]
    target = kr["target"]
    delta = kr["delta_to_target_pct"]
    delta_txt = f"{delta:+}%" if isinstance(delta,(int,float)) else str(delta)
    header = html.Div([
        html.Strong(kr["title"]),
        html.Span(status, className="badge ms-2", style={"backgroundColor":color})
    ], className="d-flex align-items-center justify-content-between")
    stats = html.Div([
        html.Span(f"Current: {current:,}"),
        html.Span(f"Target: {target:,}", className="ms-3 text-muted"),
        html.Span(f"Δ to target: {delta_txt}", className="ms-3")
    ], className="small text-muted")
    return dbc.Card(
        dbc.CardBody([
            header,
            stats,
            dcc.Graph(figure=kr_mini_chart(kr), config={"displayModeBar":False}, className="mt-2"),
            dbc.Button("Open details", size="sm", color="light",
                       id={"type":"open-kr","id":kr["id"]}, className="mt-1")
        ]),
        className="shadow-sm h-100"
    )

def kr_full_chart(kr):
    x = [p["period"] for p in kr["series"]]
    y = [p["value"] for p in kr["series"]]
    target = kr["series"][-1]["target"] if kr["series"] else kr["target"]
    fig = go.Figure()
    fig.add_bar(x=x, y=y, name="Actual")
    fig.add_scatter(x=x, y=[target]*len(x), mode="lines", name="Target", line=dict(dash="dash"))
    fig.update_layout(margin=dict(l=10,r=10,t=30,b=10), height=360, title=kr["title"])
    return fig

# ---------- App ----------
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # Expose for Gunicorn

app.title = "OKR Dashboard (Objectives → KRs)"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H3("Objectives & Key Results"), md=8),
        dbc.Col(dbc.Badge(f"Period: {DATA['period']}", color="secondary", className="float-end"), md=4),
    ], className="mt-3 mb-2"),
    dcc.Store(id="active-objective", data="OBJ-1"),
    dcc.Store(id="okr-data", data=DATA),
    html.Div(id="objectives-row", className="d-flex gap-3 flex-wrap mb-3 objectives-row"),
    html.Hr(),
    dbc.Row(id="krs-grid", className="g-3"),
    dbc.Offcanvas(
        id="kr-drawer", title="Key Result", placement="end", is_open=False, scrollable=True,
        children=[
            html.Div(id="kr-drawer-header"),
            dcc.Graph(id="kr-drawer-chart", config={"displayModeBar":False}),
            html.H6("Recent notes", className="mt-3"),
            html.Ul(id="kr-drawer-notes", className="small")
        ],
        style={"width":"520px"}
    )
], fluid=True)

# ---------- Callbacks ----------
@app.callback(
    Output("objectives-row","children"),
    Input("okr-data","data"),
    Input("active-objective","data")
)
def render_objectives(data, active_id):
    return [objective_card(o, active_id) for o in data["objectives"]]

@app.callback(
    Output("active-objective","data"),
    Input({"type":"objective-card","id":ALL},"n_clicks_timestamp"),
    State("okr-data","data"),
    State("active-objective","data"),
    prevent_initial_call=True
)
def select_objective(ts_list, data, current):
    if not ts_list or all(t is None for t in ts_list):
        raise dash.exceptions.PreventUpdate
    idx = max(range(len(ts_list)), key=lambda i: (ts_list[i] or 0))
    return data["objectives"][idx]["id"]

@app.callback(
    Output("krs-grid","children"),
    Input("active-objective","data"),
    State("okr-data","data")
)
def render_krs(active_id, data):
    krs = [k for k in data["key_results"] if k["objective_id"] == active_id]
    if not krs:
        return dbc.Alert("No Key Results defined for this Objective.", color="light")
    return [dbc.Col(kr_card(kr), lg=4, md=6, sm=12) for kr in krs]

@app.callback(
    Output("kr-drawer","is_open"),
    Output("kr-drawer","title"),
    Output("kr-drawer-chart","figure"),
    Output("kr-drawer-notes","children"),
    Output("kr-drawer-header","children"),
    Input({"type":"open-kr","id":ALL},"n_clicks"),
    State("okr-data","data"),
    prevent_initial_call=True
)
def open_kr(n_clicks_list, data):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trig = json.loads(ctx.triggered[0]["prop_id"].split(".")[0])
    kr_id = trig["id"]
    kr = next(k for k in data["key_results"] if k["id"] == kr_id)
    title = f"{kr['title']} — Owner: {kr['owner']}  ({kr['status']})"
    notes = [html.Li(f"{n['date']}: {n['text']}") for n in kr.get("notes", [])] or [html.Li("No notes yet.")]
    hdr = html.Div([
        html.Div([html.Span("Current", className="text-muted me-2"), html.Strong(f"{kr['current']:,}")]),
        html.Div([html.Span("Target", className="text-muted me-2"), html.Strong(f"{kr['target']:,}")]),
        html.Div([html.Span("Δ to target", className="text-muted me-2"), html.Strong(f"{kr['delta_to_target_pct']:+}%")]),
    ], className="d-flex gap-4 mb-2")
    return True, title, kr_full_chart(kr), notes, hdr

if __name__ == "__main__":
    # Newer Dash uses app.run(...)
    app.run(debug=True)
