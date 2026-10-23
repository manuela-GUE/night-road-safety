import pandas as pd
import streamlit as st

from utils import theme, viz
from utils.io import SOURCE_TEXT

DAY, UNLIT = "Daylight", "Night, no street lighting"


def _rate(df: pd.DataFrame) -> float:
    return 100 * df["is_fatal"].mean() if len(df) else float("nan")


def render(ctx) -> None:
    acc = ctx.acc
    theme.hero("🌙 Driving at night in France",
               "What really makes night driving dangerous, and what can you do about it? "
               "Injury accidents in France, 2015-2024.")
    u_all, d_all = ctx.acc_all[ctx.acc_all["lighting_group"] == UNLIT], ctx.acc_all[ctx.acc_all["lighting_group"] == DAY]
    if len(u_all) and len(d_all):
        ru, rd = _rate(u_all), _rate(d_all)
        theme.callout(
            f"<b>The headline:</b> on roads with <b>no street lighting at night</b>, <b>{ru:.1f}%</b> of injury accidents "
            f"are fatal, against <b>{rd:.1f}%</b> in daylight (<b>x{ru / rd:.1f}</b>). These accidents are "
            f"{100 * len(u_all) / len(ctx.acc_all):.0f}% of the total but "
            f"<b>{100 * u_all['n_killed'].sum() / ctx.acc_all['n_killed'].sum():.0f}% of deaths</b>.")

    u, d = acc[acc["lighting_group"] == UNLIT], acc[acc["lighting_group"] == DAY]
    ru, rd = _rate(u), _rate(d)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        theme.kpi("Injury accidents", f"{len(acc):,}", "selected filters", theme.CYAN)
    with c2:
        theme.kpi("People killed", f"{int(acc['n_killed'].sum()):,}", "within 30 days", theme.PINK)
    with c3:
        theme.kpi("Fatal rate, unlit night", f"{ru:.1f}%" if len(u) else "n/a",
                  f"x{ru / rd:.1f} vs daylight ({rd:.1f}%)" if len(u) and len(d) else "", theme.PINK)
    with c4:
        share_k = 100 * u["n_killed"].sum() / max(acc["n_killed"].sum(), 1)
        share_a = 100 * len(u) / max(len(acc), 1)
        theme.kpi("Unlit night: share of deaths", f"{share_k:.0f}%", f"for {share_a:.0f}% of accidents", theme.AMBER)
    st.write("")

    left, right = st.columns(2)
    with left, st.container(border=True):
        st.subheader("How deadly is an accident?")
        st.plotly_chart(viz.fatal_rate_by_lighting(acc), use_container_width=True, theme=None)
        st.caption("Bar chart: % of injury accidents with at least one death, by lighting condition. Dotted line = daylight level.")
    with right, st.container(border=True):
        st.subheader("Few accidents, many deaths")
        st.plotly_chart(viz.share_accidents_vs_deaths(acc), use_container_width=True, theme=None)
        st.caption("Grouped bars: each lighting condition's share of all accidents vs. all deaths.")

    with st.container(border=True):
        st.subheader("How has it evolved?")
        st.plotly_chart(viz.yearly_trend(acc, ctx.metric), use_container_width=True, theme=None)
        st.caption(f"Line chart: {ctx.metric.lower()} per year, night vs day (change the metric in the sidebar).")
    st.caption(SOURCE_TEXT)
