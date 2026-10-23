"""Dark 'neon' look: global CSS, hero banner and KPI cards."""
import streamlit as st

PINK, CYAN, AMBER, VIOLET = "#FF2E7E", "#2EE6D6", "#FFC857", "#8B5CF6"

CSS = """
<style>
.stApp { background: radial-gradient(circle at 15% -10%, #1B2757 0%, #0B1020 45%); }
.block-container { padding-top: 2.2rem; max-width: 1400px; }
.hero h1 { font-size: 2.5rem; font-weight: 800; margin: 0 0 .2rem 0;
  background: linear-gradient(90deg, #FF2E7E, #2EE6D6); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent; }
.hero p { color: #AEB8DE; font-size: 1.05rem; margin: 0 0 1rem 0; }
.callout { border: 1px solid rgba(255,46,126,.45); background: rgba(255,46,126,.08);
  border-radius: 14px; padding: 14px 18px; font-size: 1.05rem; margin-bottom: 1rem; }
.kpi { background: linear-gradient(145deg, #131A33, #0E1530); border: 1px solid rgba(255,255,255,.08);
  border-left: 4px solid var(--accent); border-radius: 14px; padding: 14px 18px; height: 100%;
  box-shadow: 0 0 26px color-mix(in srgb, var(--accent) 14%, transparent); }
.kpi .label { font-size: .75rem; text-transform: uppercase; letter-spacing: .09em; color: #9AA6CF; }
.kpi .value { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; line-height: 1.15; }
.kpi .sub { font-size: .85rem; color: var(--accent); }
.tip { background: linear-gradient(145deg, #131A33, #0E1530); border: 1px solid rgba(255,255,255,.08);
  border-top: 3px solid var(--accent); border-radius: 14px; padding: 16px 18px; height: 100%; }
.tip .icon { font-size: 1.6rem; } .tip h4 { margin: .3rem 0; color: #fff; } .tip p { color: #C9D1EE; margin: 0; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 14px; background: rgba(19,26,51,.55); }
h2, h3 { letter-spacing: .01em; }
</style>
"""


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)


def callout(html: str) -> None:
    st.markdown(f'<div class="callout">{html}</div>', unsafe_allow_html=True)


def kpi(label: str, value: str, sub: str = "", accent: str = PINK) -> None:
    st.markdown(f'<div class="kpi" style="--accent:{accent}"><div class="label">{label}</div>'
                f'<div class="value">{value}</div><div class="sub">{sub}&nbsp;</div></div>', unsafe_allow_html=True)


def tip(icon: str, title: str, text: str, accent: str = CYAN) -> None:
    st.markdown(f'<div class="tip" style="--accent:{accent}"><div class="icon">{icon}</div>'
                f'<h4>{title}</h4><p>{text}</p></div>', unsafe_allow_html=True)
