import json
import dash
from dash import Dash, html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

# Data with 3 objectives and KRs for each (abbreviated for brevity)
DATA = {
    "period": "2025-12",
    "objectives": [
        {"id":"OBJ-1","title":"Increase Revenue","description":"Enhance sales strategies, optimize marketing, expand reach.","owner":"Liam O'Connor","status":"At Risk","progress_pct":62},
        {"id":"OBJ-2","title":"Customer Satisfaction","description":"Streamline support, improve quality, gather feedback.","owner":"Fatima Masood","status":"Off Track","progress_pct":41},
        {"id":"OBJ-3","title":"Market Reach","description":"Boost brand visibility and customer growth.","owner":"Jamal Habib","status":"On Track","progress_pct":78},
    ],
    "key_results": [
        # Add KR entries for OBJ-1, OBJ-2, OBJ-3 (see earlier content, trimmed here)
        {"id":"KR-1","objective_id":"OBJ-1","title":"Monthly Revenue Growth ($)","unit":"$","owner":"Liam O'Connor","status":"On Track","target":30000,"current":38000,"delta_to_target_pct":30,
         "series":[{"period":"Jul 2025","value":24000,"target":30000},{"period":"Dec 2025","value":38000,"target":30000}]},
        {"id":"KR-7","objective_id":"OBJ-2","title":"CSAT Score (%)","unit":"%","owner":"Sofia Lee","status":"At Risk","target":85,"current":81,"delta_to_target_pct":-4,
         "series":[{"period":"Jul 2025","value":82,"target":85},{"period":"Dec 2025","value":81,"target":85}]},
        {"id":"KR-10","objective_id":"OBJ-3","title":"Website Visitors (K)","unit":"K","owner":"Jamal Habib","status":"On Track","target":220,"current":240,"delta_to_target_pct":9,
         "series":[{"period":"Jul 2025","value":150,"target":220},{"period":"Dec 2025","value":240,"target":220}]},
    ]
}

STAT_COLORS = {"On Track":"#10B981", "At Risk":"#F59E0B", "Off Track":"#EF4444", "Default":"#64748B"}

def objective_card(obj, active_id):
    selected = obj["id"] == active_id
    border = "border-success" if selected else "border-0"
    ring = dbc.Progress(value=obj["progress_pct"], color="primary", style={"height":"6px"})
    status_dot = html.Span(style={"display":"inline-block","width":"10px","height":"10px","borderRadius":"50%",
        "backgroundColor":STAT_COLORS.get(obj["status"], STAT_COLORS["Default"]),"marginRight":"6px"})
    return dbc.Card(dbc.CardBody([html.Div([status_dot, html.Small(obj["status"])]),
        html.H6(obj["title"], className="mt-1 mb-1"), html.P(obj["description"], className="text-muted mb-2", style={"minHeight":"44px"}), ring]),
        id={"type":"objective-card","id":obj["id"]}, className=f"shadow-sm {border} objective-card",
        style={"cursor":"pointer","minWidth":"260px"})

def kr_mini_chart(kr):
    x=[p["period"] for p in kr["series"]]; y=[p["value"] for p in kr["series"]]
    target=kr["series"][-1]["target"] if kr["series"] else kr["target"]
    colors=["#94A3B8"]*(len(y)-1)+[STAT_COLORS.get(kr["status"], STAT_COLORS["Default"])] if y else None
    fig=go.Figure(); fig.add_bar(x=x,y=y,marker_color=colors); fig.add_hline(y=target,line_dash="dash",annotation_text="Target")
    fig.update_layout(showlegend=False,margin=dict(l=0,r=0,t=0,b=0),height=180,autosize=True,uirevision="static",transition={'duration':0})
    fig.update_xaxes(fixedrange=True); fig.update_yaxes(fixedrange=True); return fig

def kr_card(kr):
    color=STAT_COLORS.get(kr["status"],STAT_COLORS["Default"]); current=kr["current"]; target=kr["target"]; delta=kr["delta_to_target_pct"]
    delta_txt=f"{delta:+}%" if isinstance(delta,(int,float)) else str(delta)
    header=html.Div([html.Strong(kr["title"]), html.Span(kr["status"],className="badge ms-2",style={"backgroundColor":color})],
        className="d-flex align-items-center justify-content-between")
    stats=html.Div([html.Span(f"Current: {current:,}"), html.Span(f"Target: {target:,}",className="ms-3 text-muted"), html.Span(f"Δ to target: {delta_txt}",className="ms-3")],className="small text-muted")
    return dbc.Card(dbc.CardBody([header, stats, dcc.Graph(id=f"kr-mini-{kr['id']}",figure=kr_mini_chart(kr),config={"displayModeBar":False,"responsive":True},className="mt-2"),
        dbc.Button("Open details",size="sm",color="light",id={"type":"open-kr","id":kr["id"]},className="mt-2")]), className="shadow-sm h-100 kr-card")

app=Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]); server=app.server; app.title="OKR Dashboard"

app.layout=dbc.Container([
    dbc.Row([dbc.Col(html.H3("Objectives & Key Results"),md=8),dbc.Col(dbc.Badge(f"Period: {DATA['period']}",color="secondary",className="float-end"),md=4)],className="mt-3 mb-2"),
    dcc.Store(id="active-objective",data="OBJ-1"), dcc.Store(id="okr-data",data=DATA),
    html.Div(id="objectives-row",className="d-flex gap-3 flex-wrap mb-3 objectives-row"), html.Hr(),
    dbc.Row(id="krs-grid",className="gx-4 gy-4")
], fluid=True)

@app.callback(Output("objectives-row","children"), Input("okr-data","data"), Input("active-objective","data"))
def render_objectives(data,active_id): return [objective_card(o,active_id) for o in data["objectives"]]

@app.callback(Output("active-objective","data"), Input({"type":"objective-card","id":ALL},"n_clicks_timestamp"), State("okr-data","data"), State("active-objective","data"), prevent_initial_call=True)
def select_objective(ts_list,data,current):
    if not ts_list or all(t is None for t in ts_list): raise dash.exceptions.PreventUpdate
    idx=max(range(len(ts_list)), key=lambda i:(ts_list[i] or 0)); return data["objectives"][idx]["id"]

@app.callback(Output("krs-grid","children"), Input("active-objective","data"), State("okr-data","data"))
def render_krs(active_id,data):
    krs=[k for k in data["key_results"] if k["objective_id"]==active_id]
    if not krs: return [dbc.Col(dbc.Alert("No Key Results for this Objective.",color="light"),width=12)]
    return [dbc.Col(kr_card(kr),lg=4,md=6,sm=12) for kr in krs]

if __name__=="__main__": app.run(debug=True)
