import streamlit as st

from utils import io as dio
from utils import viz


@st.cache_data(show_spinner=False)
def _geojson():
    return dio.load_geojson()


def render(ctx) -> None:
    acc = ctx.acc
    st.title("🔎 Deep dives")
    st.caption("Four questions a driver may ask, answered side by side. Filters in the sidebar apply to every panel.")

    a, b = st.columns(2)
    with a, st.container(border=True):
        st.subheader("When is it most severe?")
        st.plotly_chart(viz.heatmap_hour_dow(acc, ctx.metric), use_container_width=True, theme=None)
        st.caption(f"Heatmap of {ctx.metric.lower()} by hour and weekday. Early Saturday hours belong to Friday night. "
                   "Fatal-rate cells with fewer than 30 accidents are blank.")
    with b, st.container(border=True):
        st.subheader("Is it the dark, or the road?")
        label = st.radio("Compare within", ["Area type", "Road type", "Speed limit"], horizontal=True,
                         help="Comparing lighting conditions inside one category removes that category's effect.")
        by = {"Area type": "area", "Road type": "road_type", "Speed limit": "speed_limit"}[label]
        st.plotly_chart(viz.fatal_rate_within(acc, by), use_container_width=True, theme=None)
        st.caption(f"Grouped bars, same road conditions. Groups under {viz.MIN_CELL} accidents hidden; speed limit from 2019.")

    c, d = st.columns(2)
    with c, st.container(border=True):
        st.subheader("Who is most exposed?")
        who = st.radio("Break down by", list(viz.GROUPS), horizontal=True)
        st.plotly_chart(viz.killed_rate_by(ctx.users, who), use_container_width=True, theme=None)
        st.caption("Share of users killed among everyone involved in injury accidents (year and department filters only). "
                   "Compare bars within a group (day vs night), not across groups: pedestrians in injury accidents are "
                   "rarely unhurt, which raises their base rate.")
    with d, st.container(border=True):
        st.subheader("Which departments are the worst at night?")
        table = viz.dep_table(acc, _geojson(), "Night, no street lighting")
        st.plotly_chart(viz.top_departments(table), use_container_width=True, theme=None)
        st.caption("Top 10 metropolitan departments by fatal-accident rate on unlit night roads (min. 30 accidents). See the Map page.")