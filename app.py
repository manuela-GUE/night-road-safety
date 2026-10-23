from types import SimpleNamespace

import streamlit as st

from sections import action, data_quality, deep_dives, map_page, overview
from utils import io as dio
from utils import theme
from utils.viz import METRICS

st.set_page_config(page_title="Night Driving Safety - France", page_icon="🌙", layout="wide")
theme.apply()


@st.cache_data(show_spinner="Loading data...")
def get_data():
    return dio.load_processed()


try:
    acc, users, quality = get_data()
except FileNotFoundError:
    st.error("Processed data not found. Run `python build_data.py` first (see README).")
    st.stop()

with st.sidebar:
    st.header("🎛️ Filters")
    y_min, y_max = int(acc["year"].min()), int(acc["year"].max())
    years = st.slider("Years", y_min, y_max, (y_min, y_max))
    deps = st.multiselect("Departments (empty = all)", sorted(acc["dep"].dropna().unique()))
    areas = st.multiselect("Area type (empty = all)", sorted(acc["area"].dropna().unique()))
    metric = st.selectbox("Metric (trend & heatmap)", METRICS, help="Variable shown in the trend chart and the heatmap.")

mask = acc["year"].between(*years)
if deps:
    mask &= acc["dep"].isin(deps)
if areas:
    mask &= acc["area"].isin(areas)
acc_f = acc[mask]
users_f = users[users["year"].between(*years) & (users["dep"].isin(deps) if deps else True)]
if acc_f.empty:
    st.warning("No accidents match the current filters.")
    st.stop()

ctx = SimpleNamespace(acc=acc_f, acc_all=acc, users=users_f, users_all=users, quality=quality, metric=metric)
pages = [
    st.Page(lambda: overview.render(ctx), title="Overview", icon="🌙", url_path="overview", default=True),
    st.Page(lambda: deep_dives.render(ctx), title="Deep dives", icon="🔎", url_path="deep-dives"),
    st.Page(lambda: map_page.render(ctx), title="Map", icon="🗺️", url_path="map"),
    st.Page(lambda: action.render(ctx), title="What can I do?", icon="🧭", url_path="action"),
    st.Page(lambda: data_quality.render(ctx), title="Data & limits", icon="🧪", url_path="data"),
]
st.navigation(pages, position="top").run()

