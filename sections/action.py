import pandas as pd
import streamlit as st

from utils import theme

DAY, UNLIT = "Daylight", "Night, no street lighting"


def excess_deaths(acc: pd.DataFrame) -> float:
    """Deaths on unlit night roads above what the daylight deaths-per-accident rate would give,
    computed separately for built-up and non-built-up areas (so urban/rural mix does not bias it)."""
    g = acc.groupby(["area", "lighting_group"], observed=True).agg(n=("num_acc", "size"), k=("n_killed", "sum"))
    total = 0.0
    for area in g.index.get_level_values(0).unique():
        if (area, DAY) in g.index and (area, UNLIT) in g.index and g.loc[(area, DAY), "n"] > 0:
            day, unlit = g.loc[(area, DAY)], g.loc[(area, UNLIT)]
            total += max(unlit["k"] - unlit["n"] * day["k"] / day["n"], 0)
    return total


def _facts(a: pd.DataFrame) -> dict:
    """Numbers behind the advice cards, computed on the full data set."""
    out = {}
    r = a.groupby(["area", "lighting_group"], observed=True)["is_fatal"].mean()
    ratios = [r[(ar, UNLIT)] / r[(ar, DAY)] for ar in ("Built-up area", "Outside built-up area")
              if (ar, UNLIT) in r.index and (ar, DAY) in r.index]
    out["ratio_lo"], out["ratio_hi"] = (min(ratios), max(ratios)) if ratios else (float("nan"),) * 2
    h = a.groupby("hour").agg(n=("num_acc", "size"), f=("is_fatal", "mean"))
    top = h[h["n"] >= 1000].nlargest(3, "f")
    out["hours"] = ", ".join(f"{int(i)}h" for i in sorted(top.index))
    out["hour_rate"] = 100 * top["f"].mean()
    n = a[a["is_night"]].groupby("dow")["n_killed"].sum()
    out["weekend_share"] = 100 * n.reindex([4, 5, 6]).sum() / max(n.sum(), 1)
    return out


def _killed_rates(users: pd.DataFrame, groups: tuple, min_users: int = 200) -> dict:
    """{group: (daylight %, unlit-night %)} share of users killed; NaN when the sample is too small."""
    d = users[users["severity"] != "Unknown"]
    out = {}
    for g in groups:
        s = d[d["veh_group"] == g]
        rates = []
        for lg in (DAY, UNLIT):
            t = s.loc[s["lighting_group"] == lg, "n"].sum()
            k = s.loc[(s["lighting_group"] == lg) & (s["severity"] == "Killed"), "n"].sum()
            rates.append(100 * k / t if t >= min_users else float("nan"))
        out[g] = tuple(rates)
    return out


def _age_rates(users: pd.DataFrame, min_users: int = 200):
    """(65+ daylight %, 65+ unlit-night %, 25-49 unlit-night %) share of users killed."""
    d = users[(users["severity"] != "Unknown") & users["age_band"].isin(["25-34", "35-49", "65+"])]

    def rate(bands, lg):
        s = d[d["age_band"].isin(bands) & (d["lighting_group"] == lg)]
        t = s["n"].sum()
        return 100 * s.loc[s["severity"] == "Killed", "n"].sum() / t if t >= min_users else float("nan")
    return rate(["65+"], DAY), rate(["65+"], UNLIT), rate(["25-34", "35-49"], UNLIT)


def _pct(x: float) -> str:
    return "n/a" if x != x else f"{x:.0f}%"


def render(ctx) -> None:
    st.title("🧭 What can I do?")
    f = _facts(ctx.acc_all)
    c1, c2, c3 = st.columns(3)
    with c1:
        theme.tip("🛣️", "Slow down on unlit roads",
                  f"At night without street lighting, an accident is {f['ratio_lo']:.1f} to {f['ratio_hi']:.1f} times more "
                  "likely to be fatal than in daylight on the same type of area. Adapt your speed to what your headlights "
                  "can show you.", theme.PINK)
    with c2:
        theme.tip("🕒", "Beware the small hours",
                  f"Accidents are rarer between {f['hours']}, but the most severe: about {f['hour_rate']:.0f}% are fatal. "
                  "Fatigue is a likely factor, so plan breaks or avoid driving then.", theme.CYAN)
    with c3:
        theme.tip("🎉", "Weekend nights count double",
                  f"Friday to Sunday carry {f['weekend_share']:.0f}% of all night deaths. "
                  "Plan your way home before you go out.", theme.AMBER)
    v = _killed_rates(ctx.users_all, ("Pedestrian", "Bicycle", "Motorcycle", "Moped (<=50cc)"))
    st.write("")
    c4, c5, c6 = st.columns(3)
    old_d, old_u, ref_u = _age_rates(ctx.users_all)
    with c4:
        theme.tip("🚶", "Expect people you cannot see",
                  f"On unlit night roads, {_pct(v['Pedestrian'][1])} of pedestrians and {_pct(v['Bicycle'][1])} of cyclists "
                  f"involved in an injury accident are killed, against {_pct(v['Pedestrian'][0])} and "
                  f"{_pct(v['Bicycle'][0])} in daylight. Drive so that you can stop within the distance you can see.",
                  theme.VIOLET)
    with c5:
        theme.tip("🏍️", "Two-wheelers: make yourself visible",
                  f"Motorcyclists involved in an accident on unlit night roads are killed in {_pct(v['Motorcycle'][1])} of "
                  f"cases ({_pct(v['Motorcycle'][0])} by day), mopeds in {_pct(v['Moped (<=50cc)'][1])} "
                  f"({_pct(v['Moped (<=50cc)'][0])} by day). The data shows the gap, not its cause: working lights and "
                  "reflective gear are standard prevention advice.", theme.PINK)
    with c6:
        ratio = f"{old_u / ref_u:.1f}x" if ref_u == ref_u and old_u == old_u and ref_u > 0 else "much higher"
        theme.tip("👵", "Age changes the outcome",
                  f"Among people aged 65+ involved in an accident on an unlit night road, {_pct(old_u)} are killed "
                  f"({_pct(old_d)} by day): {ratio} the rate of 25-49 year-olds ({_pct(ref_u)}). This reflects physical "
                  "fragility, not how often older drivers have accidents, which this data cannot tell.", theme.AMBER)
    st.caption("Advice is derived from statistics on all years of data; it shows associations, not proven causes.")

    st.header("What if unlit night roads were as safe as daylight?")
    with st.container(border=True):
        st.caption("Scenario, not a forecast: it assumes part of the gap to daylight (same area type) could be closed. "
                   "That is optimistic, because some of the gap may come from fatigue, alcohol or speed rather than light.")
        closed = st.slider("Share of the gap that is closed", 0, 100, 25, step=5, format="%d%%")
        saved = closed / 100 * excess_deaths(ctx.acc) / max(ctx.acc["year"].nunique(), 1)
        theme.kpi("Deaths avoided per year", f"{saved:,.0f}", "for the selected filters", theme.CYAN)