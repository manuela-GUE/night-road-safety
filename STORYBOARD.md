# Storyboard and demo-video script

Project: *Driving at night in France: what really makes it dangerous?*
Live app: https://night-road-safety-france.streamlit.app/ - Author: GUE (BIA)

## 1. Audience, questions, takeaways

**Audience.** Drivers (car and two-wheelers) who sometimes drive at night. Secondary audience: road-prevention teams.

| Driver's question | Where it is answered | Takeaway |
|---|---|---|
| Is night driving really more dangerous? | Overview | Not because of the dark itself: unlit roads at night are where accidents turn deadly (13.5% fatal vs 4.9% in daylight) |
| Is it the dark or the road? | Deep dives, "Is it the dark, or the road?" | The gap holds within every area type, road type and speed limit |
| When is it worst? | Deep dives, heatmap | Small hours (about 3-5 am) and Friday-Sunday nights |
| Who is most exposed? | Deep dives, "Who?" | Pedestrians, cyclists, mopeds, people aged 65+ |
| Where? | Map, top 10 | Rural departments with many unlit roads |
| What can I do? | What can I do? | Slow down on unlit roads, avoid the small hours, be visible, expect vulnerable users |

## 2. Story arc

| Stage | Page | Message |
|---|---|---|
| Hook | Overview (headline box, KPIs) | One sentence: x2.8 more fatal on unlit night roads; 10.6% of accidents but 25.8% of deaths |
| Context | Overview (two charts, trend) | Severity by lighting; few accidents but many deaths; stable over 2015-2024, 2020 lockdown dip |
| Key insights | Deep dives + Map | When, same-conditions check, who, where |
| Implications | What can I do? | Six tips grounded in the numbers; what-if slider |
| Trust | Data & limits | Quality checks per year; severity not risk per km; association not causation |

## 3. Page-by-page storyboard

| Page | Headline | Visuals and interaction | Why it is there |
|---|---|---|---|
| Overview | "It is not darkness itself: it is unlit roads" | 4 KPI cards (accidents, deaths, fatal rate unlit night, share of deaths); bar chart by lighting with daylight reference line; grouped bars share of accidents vs deaths; yearly line chart with COVID annotation. Sidebar: years, departments, area type, metric | Hook and context; KPIs react to the filters |
| Deep dives | Four questions, one screen | Heatmap hour x weekday; grouped bars "same conditions" (radio: area / road / speed); "who" bars (radio: vehicle / age / trip); top-10 departments | Insights without scrolling or switching tabs |
| Map | "Where is it most severe?" | Choropleth by metropolitan department, selector for lighting condition, top-10 bars | Spatial comparison |
| What can I do? | "What can I do?" | Six tip cards with computed numbers; slider "share of the gap closed" -> deaths avoided per year | Implications and what-if |
| Data & limits | "Data quality and limitations" | Line chart of quality checks per year; validation table; limitations list | Transparency |

Design: dark navy background with pink (unlit night, the "danger" colour), cyan (lit night) and amber (daylight) so the same colour means the same condition on every chart. Top navigation keeps each page to one screen.

## 4. Demo video script (target 3:15, limit 4:00)

Record at the default filters (all years, all departments) so the numbers below match the screen. Read the exact values on screen before saying them.

| Time | On screen | Narration |
|---|---|---|
| 0:00-0:20 | Overview, headline box | "Every year, thousands of people die on French roads. We often blame the night. But is it the darkness, or the roads we drive on at night? I analysed ten years of police-recorded injury accidents, 564,000 of them, to find out." |
| 0:20-0:50 | KPI cards, then the two charts | "On roads with no street lighting at night, about 13.5% of injury accidents are fatal, against 4.9% in daylight: nearly three times more. These accidents are 10.6% of the total but 25.8% of deaths. Night with street lighting is not the problem." |
| 0:50-1:05 | Trend chart, sidebar metric | "The pattern is stable over the years. The dip in 2020 is the lockdowns. I can switch the metric here, and filter by years, departments or area type; the KPIs follow." |
| 1:05-1:25 | Deep dives: heatmap | "When? Switching the metric to fatal accidents shows the small hours, around 3 to 5 am, as the most severe, and Friday to Sunday nights carry more than half of night deaths." |
| 1:25-1:50 | Deep dives: same conditions (radio: Area type, then Road type) | "But maybe unlit roads are simply rural roads? I compare like with like. In towns, 7.9% versus 2.5%; outside towns, 14.9% versus 9.3%. The gap holds on every road type and speed limit, so it is not just the countryside." |
| 1:50-2:10 | Deep dives: who (Vehicle, then Age band) | "Who? Once an accident happens on an unlit night road, pedestrians and cyclists are the most likely to die, then mopeds and motorcycles. People aged 65 and over are about twice as likely to die as 25 to 49 year-olds." |
| 2:10-2:30 | Map page | "Where? This map shows the fatal rate on unlit night roads by department; the top 10 on the right helps target prevention. I can switch to daylight to compare." |
| 2:30-2:55 | What can I do? tips, then slider | "What can a driver do? Slow down on unlit roads, avoid the small hours, expect people you cannot see, and be visible on two wheels. And if we closed just a quarter of the gap with daylight, this slider estimates how many lives per year could be saved. It is a scenario, not a forecast." |
| 2:55-3:15 | Data & limits | "The data only covers injury accidents and has no traffic counts, so I compare severity, not risk per kilometre. GPS is unreliable before 2018, so the map uses departments. And these are associations, not proof of cause. Thank you." |

## 5. Recording checklist

- Open the app a few minutes before recording so it is awake (free hosting sleeps after inactivity).
- Browser zoom 100% or 110%, window in full screen, notifications off.
- Rehearse once; keep to 3 to 4 minutes (the subject asks for 2 to 4).
- Move the mouse slowly and point at what you mention; pause 1 second after each click.
- Upload the video (YouTube unlisted, Drive or similar), check the link works in a private window, and put it in the submission.
- Submission: app URL, repository link (code + README + this storyboard), video link, and the zip.
