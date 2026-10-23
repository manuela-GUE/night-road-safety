import pandas as pd
import plotly.express as px
import streamlit as st

from utils import viz


def render(ctx) -> None:
    st.title("🧪 Data quality & limitations")
    q = pd.DataFrame(ctx.quality).set_index("year")
    with st.container(border=True):
        st.subheader("Missing or unusable values, by year")
        cols = [c for c in ("gps_invalid_pct", "users_age_unknown_pct", "dep_invalid_pct", "hour_missing_pct") if c in q]
        fig = px.line(q[cols].reset_index().melt("year", var_name="check", value_name="% of rows"), x="year",
                      y="% of rows", color="check", markers=True, labels={"year": "Year"},
                      color_discrete_sequence=["#FF2E7E", "#2EE6D6", "#FFC857", "#8B5CF6"])
        fig.update_xaxes(dtick=1)
        st.plotly_chart(viz._style(fig, 320), use_container_width=True, theme=None)
        st.caption("Line chart: share of rows failing each check. GPS is mostly unusable before 2018.")
        with st.expander("Full validation table"):
            st.dataframe(q, use_container_width=True)
    st.info(
        "- BAAC only covers **injury accidents reported by police**: there is no traffic data, so we compare "
        "*severity*, not risk per kilometre.\n"
        "- 'Killed' = died within 30 days. Night = BAAC lighting codes 3-5 (4 = lighting switched off, grouped with unlit).\n"
        "- GPS coordinates are invalid for about half of the 2015 accidents and ~0% from 2019, so maps use departments.\n"
        "- Unknown user age jumps from ~0% to ~2% from 2021. Speed limit exists only from 2019.\n"
        "- National figures include overseas departments and territories; maps and department rankings cover metropolitan France only.\n"
        "- Lit roads are mostly in towns, so raw day/night comparisons mix road type with light: see 'Deep dives'.\n"
        "- Association is not causation: fatigue, alcohol and actual speed also differ at night.")