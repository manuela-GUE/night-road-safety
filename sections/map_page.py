import streamlit as st

from utils import io as dio
from utils import viz
from utils.prep import LIGHTING_ORDER


@st.cache_data(show_spinner=False)
def _geojson():
    return dio.load_geojson()


def render(ctx) -> None:
    st.title("🗺️ Where is it most severe?")
    group = st.selectbox("Lighting condition", LIGHTING_ORDER, index=LIGHTING_ORDER.index("Night, no street lighting"))
    table = viz.dep_table(ctx.acc, _geojson(), group)
    if table.empty:
        st.warning("Not enough accidents for this selection.")
        return
    left, right = st.columns([3, 2])
    with left, st.container(border=True):
        st.plotly_chart(viz.dep_map(table, _geojson()), use_container_width=True, theme=None)
        st.caption("Map of metropolitan France: share of injury accidents that are fatal, by department. "
                   "Hover for details. Departments with fewer than 30 accidents are not coloured. Overseas departments and territories are excluded here (very small samples).")
    with right, st.container(border=True):
        st.subheader("Top 10 departments")
        st.plotly_chart(viz.top_departments(table), use_container_width=True, theme=None)
        st.caption("Bar chart: ten highest fatal-accident rates for the selected lighting condition.")