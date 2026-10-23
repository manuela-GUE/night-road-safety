"""Chart functions: one place to keep colours, labels and hover text consistent (dark theme)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.prep import AGE_LABELS, LIGHTING_ORDER, TRIP

COLORS = {"Daylight": "#FFC857", "Dawn / dusk": "#FF8A4C",
          "Night, street lighting on": "#2EE6D6", "Night, no street lighting": "#FF2E7E"}
SCALE = [[0, "#2A3B8F"], [0.5, "#8B3FD9"], [1, "#FF2E7E"]]
METRICS = ["Accidents", "People killed", "Fatal accidents (%)"]
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SPEEDS = [30, 50, 80, 90, 110, 130]
VEHICLES = ["Car", "Motorcycle", "Moped (<=50cc)", "Bicycle", "Pedestrian", "Van", "Truck"]
MIN_CELL = 200  # hide rates computed on fewer accidents / users than this
FATAL_LABEL = "Fatal accidents (%)"


def _style(fig: go.Figure, height: int = 380) -> go.Figure:
    grid = "rgba(255,255,255,0.08)"
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#E8ECF8", size=13), height=height, margin=dict(l=10, r=10, t=50, b=10),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""))
    fig.update_xaxes(gridcolor=grid, zeroline=False)
    fig.update_yaxes(gridcolor=grid, zeroline=False)
    return fig


def fatal_rate_by_lighting(acc: pd.DataFrame) -> go.Figure:
    g = (acc.groupby("lighting_group", observed=True)
         .agg(accidents=("num_acc", "size"), fatal=("is_fatal", "sum")).reindex(LIGHTING_ORDER).dropna().reset_index())
    g["rate"] = 100 * g["fatal"] / g["accidents"]
    fig = px.bar(g, x="lighting_group", y="rate", color="lighting_group", color_discrete_map=COLORS,
                 text=g["rate"].round(1).astype(str) + "%", hover_data={"accidents": ":,", "fatal": ":,", "rate": ":.2f"},
                 labels={"lighting_group": "Lighting condition", "rate": FATAL_LABEL})
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False)
    fig.update_yaxes(range=[0, float(g["rate"].max()) * 1.2])
    day = g.loc[g["lighting_group"] == "Daylight", "rate"]
    if len(day):
        fig.add_hline(y=float(day.iloc[0]), line_dash="dot", line_color="#AEB8DE")
    return _style(fig)


def share_accidents_vs_deaths(acc: pd.DataFrame) -> go.Figure:
    g = (acc.groupby("lighting_group", observed=True).agg(a=("num_acc", "size"), k=("n_killed", "sum"))
         .reindex(LIGHTING_ORDER).dropna())
    g = pd.DataFrame({"Share of accidents": 100 * g["a"] / g["a"].sum(), "Share of deaths": 100 * g["k"] / g["k"].sum()})
    long = g.reset_index().melt("lighting_group", var_name="measure", value_name="pct")
    fig = px.bar(long, x="lighting_group", y="pct", color="measure", barmode="group",
                 color_discrete_map={"Share of accidents": "#6C7AA8", "Share of deaths": "#FF2E7E"},
                 text=long["pct"].round(0).astype(int).astype(str) + "%",
                 labels={"lighting_group": "Lighting condition", "pct": "% of total"})
    fig.update_traces(textposition="outside")
    return _style(fig)


def yearly_trend(acc: pd.DataFrame, metric: str) -> go.Figure:
    d = acc.assign(period=acc["is_night"].map({True: "Night", False: "Day / dawn / dusk"}))
    g = d.groupby(["year", "period"]).agg(accidents=("num_acc", "size"), killed=("n_killed", "sum"),
                                          fatal=("is_fatal", "sum")).reset_index()
    g["Fatal accidents (%)"] = 100 * g["fatal"] / g["accidents"]
    g = g.rename(columns={"accidents": "Accidents", "killed": "People killed"})
    fig = px.line(g, x="year", y=metric, color="period", markers=True,
                  color_discrete_map={"Night": "#FF2E7E", "Day / dawn / dusk": "#FFC857"},
                  labels={"year": "Year", "period": ""})
    fig.update_xaxes(dtick=1)
    if g["year"].eq(2020).any():
        fig.add_vline(x=2020, line_dash="dot", line_color="#AEB8DE", annotation_text="COVID-19 lockdowns",
                      annotation_position="top left")
    return _style(fig, 340)


def heatmap_hour_dow(acc: pd.DataFrame, metric: str) -> go.Figure:
    g = acc.groupby(["hour", "dow"]).agg(n=("num_acc", "size"), k=("n_killed", "sum"), f=("is_fatal", "mean"))
    col = {"Accidents": "n", "People killed": "k", "Fatal accidents (%)": "f"}[metric]
    z = g[col].unstack("dow").reindex(index=range(24), columns=range(7))
    if col == "f":
        n = g["n"].unstack("dow").reindex(index=range(24), columns=range(7))
        z = (100 * z).where(n >= 30)
    fig = px.imshow(z.values, x=DOW, y=list(range(24)), aspect="auto", color_continuous_scale=SCALE,
                    labels=dict(x="Weekday", y="Hour of day", color=metric))
    fig.update_yaxes(dtick=3)
    return _style(fig, 400)


def fatal_rate_within(acc: pd.DataFrame, by: str) -> go.Figure:
    """Fatal-accident rate by lighting, inside each category of `by` (area, road_type, speed_limit)."""
    d = acc[acc["speed_limit"].isin(SPEEDS)] if by == "speed_limit" else acc
    g = (d.groupby([by, "lighting_group"], observed=True)
         .agg(accidents=("num_acc", "size"), fatal=("is_fatal", "sum")).reset_index())
    g = g[g["accidents"] >= MIN_CELL].sort_values(by)
    g["rate"] = 100 * g["fatal"] / g["accidents"]
    g[by] = g[by].astype(int).astype(str) + " km/h" if by == "speed_limit" else g[by].astype(str)
    labels = {"area": "Area type", "road_type": "Road type", "speed_limit": "Posted speed limit"}
    fig = px.bar(g, x=by, y="rate", color="lighting_group", barmode="group", color_discrete_map=COLORS,
                 category_orders={"lighting_group": LIGHTING_ORDER}, hover_data={"accidents": ":,", "rate": ":.1f"},
                 labels={by: labels[by], "rate": FATAL_LABEL})
    return _style(fig, 340)


GROUPS = {"Vehicle / road user": ("veh_group", VEHICLES), "Age band": ("age_band", AGE_LABELS),
          "Trip purpose": ("trip", [v for v in TRIP.values()])}


def killed_rate_by(users: pd.DataFrame, label: str) -> go.Figure:
    """Share of users killed among all users involved in injury accidents, by lighting and a user attribute."""
    col, order = GROUPS[label]
    d = users[users[col].isin(order) & (users["severity"] != "Unknown")]
    keys = [col, "lighting_group"]
    tot = d.groupby(keys, observed=True)["n"].sum().rename("users")
    kil = d[d["severity"] == "Killed"].groupby(keys, observed=True)["n"].sum().rename("killed")
    g = pd.concat([tot, kil], axis=1).fillna(0).reset_index()
    g = g[g["users"] >= MIN_CELL]
    g["rate"] = 100 * g["killed"] / g["users"]
    fig = px.bar(g, x=col, y="rate", color="lighting_group", barmode="group", color_discrete_map=COLORS,
                 category_orders={"lighting_group": LIGHTING_ORDER, col: order},
                 hover_data={"users": ":,", "killed": ":,", "rate": ":.2f"},
                 labels={col: label, "rate": "Users killed (%)"})
    return _style(fig, 340)


def dep_names(geojson: dict) -> dict[str, str]:
    return {f["properties"]["code"]: f["properties"]["nom"] for f in geojson["features"]}


def dep_table(acc: pd.DataFrame, geojson: dict, group: str, min_acc: int = 30) -> pd.DataFrame:
    """Fatal-accident rate per department for one lighting condition (small samples hidden)."""
    t = (acc[acc["lighting_group"] == group].groupby("dep", observed=True)
         .agg(accidents=("num_acc", "size"), fatal=("is_fatal", "sum"), killed=("n_killed", "sum")).reset_index())
    t = t[t["accidents"] >= min_acc].copy()
    t["rate"] = 100 * t["fatal"] / t["accidents"]
    t["dep"] = t["dep"].astype(str)
    names = dep_names(geojson)
    t = t[t["dep"].isin(names)].copy()  # metropolitan departments only (overseas: tiny samples, no outline)
    t["name"] = t["dep"].map(names)
    return t


def _rings(geom: dict) -> list:
    """Outer rings of a (Multi)Polygon geometry."""
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [poly[0] for poly in geom["coordinates"]]


def dep_map(table: pd.DataFrame, geojson: dict, height: int = 560) -> go.Figure:
    """Choropleth of France drawn as filled polygons on plain axes: no tile server, CDN or API token needed."""
    rates = table.set_index("dep")
    lo, hi = float(table["rate"].min()), float(table["rate"].max())
    fig = go.Figure()
    for feat in geojson["features"]:
        code = feat["properties"]["code"]
        if code.startswith("97"):
            continue
        xs, ys = [], []
        for ring in _rings(feat["geometry"]):
            xs += [pt[0] for pt in ring] + [None]
            ys += [pt[1] for pt in ring] + [None]
        if code in rates.index:
            r = rates.loc[code]
            t = 0.5 if hi == lo else (r["rate"] - lo) / (hi - lo)
            color = px.colors.sample_colorscale(SCALE, [float(t)])[0]
            text = (f"<b>{feat['properties']['nom']}</b> ({code})<br>Fatal accidents: {r['rate']:.1f}%"
                    f"<br>{int(r['fatal']):,} of {int(r['accidents']):,} accidents")
        else:
            color, text = "#1A2244", f"<b>{feat['properties']['nom']}</b> ({code})<br>Not enough accidents"
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor=color, hoveron="fills",
                                 line=dict(color="#0B1020", width=0.6), text=text, hoverinfo="text", showlegend=False))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", hoverinfo="skip", showlegend=False,
                             marker=dict(colorscale=SCALE, cmin=lo, cmax=hi, color=[lo], showscale=True,
                                         colorbar=dict(title="Fatal (%)", thickness=14, len=0.7))))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False, scaleanchor="x", scaleratio=1.44)  # 1 deg lat ~ 1.44 deg lon at 46N
    return _style(fig, height).update_layout(margin=dict(l=0, r=0, t=10, b=0))


def top_departments(table: pd.DataFrame, n: int = 10) -> go.Figure:
    t = table.nlargest(n, "rate").sort_values("rate")
    fig = px.bar(t, x="rate", y="name", orientation="h", text=t["rate"].round(1).astype(str) + "%",
                 hover_data={"accidents": ":,", "fatal": ":,", "rate": ":.1f", "name": False},
                 labels={"rate": FATAL_LABEL, "name": ""}, color_discrete_sequence=["#FF2E7E"])
    fig.update_traces(textposition="outside")
    fig.update_xaxes(range=[0, float(t["rate"].max()) * 1.2])
    return _style(fig, 340)