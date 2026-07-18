"""Phase 3 · build the IEA/Statista market-trend assets to ingest into the RAG.

Produces, from REAL public figures (each source-cited):
  data/market_trends.jsonl        text docs (IEA Global EV Outlook, BNEF, India MoHI)
  data/market_charts/*.png        6 chart 'visual layouts' rendered from the same data

Sources (accessed Jul 2026):
  - IEA Global EV Outlook 2024/2025 — electric bus stock, sales, targets, China share
    https://www.iea.org/reports/global-ev-outlook-2025/trends-in-heavy-duty-electric-vehicles
    https://www.iea.org/reports/global-ev-outlook-2024/outlook-for-electric-mobility
  - BloombergNEF — lithium-ion battery pack price survey (2023 $139, 2024 $115, 2025 $108/kWh)
  - India Ministry of Heavy Industries / PM E-DRIVE — public charging stations (25,202, Dec 2024)

Figures that are PROJECTIONS (IEA STEPS/APS) or approximate are labelled as such.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CHARTS = DATA / "market_charts"
CHARTS.mkdir(parents=True, exist_ok=True)

IEA24 = "IEA Global EV Outlook 2024"
IEA25 = "IEA Global EV Outlook 2025 (Trends in heavy-duty EVs)"
BNEF = "BloombergNEF Battery Price Survey"
MOHI = "India Ministry of Heavy Industries / PM E-DRIVE"

# --------------------------------------------------------------------------- #
#  1. TEXT MARKET-TREND DOCUMENTS (real, sourced)
# --------------------------------------------------------------------------- #
TRENDS = [
    ("iea_india_stock", IEA25,
     "India's electric bus stock grew from under 3,000 in 2020 to over 11,500 by end of 2024. "
     "In 2024 India was the world's second-largest electric bus market by sales volume, with 3,200+ units sold."),
    ("iea_india_targets", IEA25,
     "India's National Electric Bus Programme targets 40,000 electric buses by 2027. The Bharat Urban "
     "Megabus Mission aims to introduce 100,000 electric buses to cities with population over 1 million. "
     "The PM E-DRIVE scheme supports replacement of ageing public buses."),
    ("iea_india_fund", IEA24,
     "India aims to reach a stock of 50,000 electric buses by 2027, supported by a USD 390 million fund "
     "backed by the Indian and US governments to provide loans expanding electric bus manufacturing."),
    ("iea_india_salesshare", IEA24,
     "IEA projects India's electric bus sales share rises to about 35% in 2030 and 60% in 2035 in both the "
     "STEPS and APS scenarios (projection, not actuals)."),
    ("iea_global_ebus", IEA25,
     "Global electric bus sales exceeded 70,000 units in 2024, up 30% year-over-year. Electric buses were "
     "about 3% of total global bus sales in 2023. Under stated policies the electric bus stock rises "
     "sevenfold by 2035."),
    ("iea_china_dominance", IEA25,
     "China deployed over 680,000 electric buses, with almost 70% installed before 2020. China's share of "
     "global electric bus sales fell from ~99% in 2017 to under 70% in 2024. China exported over 15,000 "
     "electric buses in 2024, a 25% increase versus 2023."),
    ("iea_europe_us", IEA25,
     "In Europe the 2024 electric bus sales share exceeded 13% and reached nearly 50% of new city buses. "
     "In the United States electric bus sales fell ~40% from their prior peak; school buses are ~50% of stock."),
    ("bnef_battery_price", BNEF,
     "Lithium-ion battery pack prices fell to a record low of USD 139/kWh in 2023 (-14%), USD 115/kWh in 2024 "
     "(-20%, the largest drop since 2017), and USD 108/kWh in 2025 — roughly 93% below 2010 levels "
     "(~USD 1,183/kWh). Drivers: LFP chemistry adoption, manufacturing overcapacity, economies of scale."),
    ("mohi_charging", MOHI,
     "India had about 25,202 public EV charging stations by December 2024. The PM E-DRIVE scheme allocates "
     "Rs 10,900 crore over two years, including Rs 2,000 crore specifically for public charging stations."),
    ("supply_chain_risk", BNEF + " / " + IEA25,
     "Battery supply chains remain concentrated: China dominates cell manufacturing and LFP cathode supply, "
     "and holds the vast majority of the global electric bus fleet. Falling pack prices help tender economics "
     "but do not remove single-country component dependence risk for Indian OEMs."),
]

with open(DATA / "market_trends.jsonl", "w", encoding="utf-8") as f:
    for doc_id, source, text in TRENDS:
        doc = {
            "doc_id": f"mkt_{doc_id}",
            "modality": "market_text",
            "file_path": "",
            "text_for_index": text,
            "metadata": {"source": source, "asset_type": "market_trend_text"},
        }
        f.write(json.dumps(doc, ensure_ascii=False) + "\n")
print(f"Wrote {DATA/'market_trends.jsonl'} ({len(TRENDS)} docs)")

# --------------------------------------------------------------------------- #
#  2. CHART 'VISUAL LAYOUTS' rendered from the same real data
# --------------------------------------------------------------------------- #
def save(fig, name):
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  chart:", name)

# 1 India e-bus stock & targets (milestones)
fig, ax = plt.subplots(figsize=(7, 4))
labels = ["2020\nstock", "2024\nstock", "2027 target\n(Nat'l EBP)", "Bharat Megabus\nMission"]
vals = [3000, 11500, 40000, 100000]
bars = ax.bar(labels, vals, color=["#95a5a6", "#2e86de", "#27ae60", "#16a085"])
ax.set_ylabel("Electric buses (units)")
ax.set_title("India electric-bus stock & deployment targets\nSource: IEA Global EV Outlook 2024/2025")
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width()/2, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
save(fig, "chart_india_ebus_stock_targets.png")

# 2 India e-bus sales-share projection
fig, ax = plt.subplots(figsize=(7, 4))
yrs = [2024, 2030, 2035]
share = [4, 35, 60]  # 2024 approx low base; 2030/2035 are IEA STEPS/APS projections
ax.plot(yrs, share, marker="o", color="#8e44ad", lw=2)
for x, y in zip(yrs, share):
    ax.text(x, y+1.5, f"{y}%", ha="center", fontsize=9)
ax.set_ylabel("Electric share of bus sales (%)")
ax.set_title("India electric-bus sales share — IEA projection (STEPS/APS)\n2030 & 2035 are projections")
ax.set_xticks(yrs); ax.set_ylim(0, 70)
save(fig, "chart_india_ebus_salesshare.png")

# 3 China share of global e-bus sales
fig, ax = plt.subplots(figsize=(7, 4))
yrs = [2017, 2024]
sh = [99, 70]
ax.plot(yrs, sh, marker="o", color="#c0392b", lw=2)
for x, y in zip(yrs, sh):
    ax.text(x, y+1, f"~{y}%", ha="center", fontsize=9)
ax.set_ylabel("China % of global e-bus sales")
ax.set_title("China's share of global electric-bus sales is falling\nSource: IEA Global EV Outlook 2025")
ax.set_xticks(yrs); ax.set_ylim(0, 105)
save(fig, "chart_china_ebus_share.png")

# 4 Battery pack price trend
fig, ax = plt.subplots(figsize=(7, 4))
yrs = [2010, 2023, 2024, 2025]
price = [1183, 139, 115, 108]
ax.plot(yrs, price, marker="o", color="#e67e22", lw=2)
for x, y in zip(yrs, price):
    ax.text(x, y+40, f"${y}", ha="center", fontsize=9)
ax.set_ylabel("Li-ion pack price (USD/kWh)")
ax.set_title("Lithium-ion battery pack price decline\nSource: BloombergNEF")
ax.set_xticks(yrs)
save(fig, "chart_battery_price_trend.png")

# 5 China vs India e-bus stock 2024 (scale gap / supply-chain)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(["China", "India"], [680000, 11500], color=["#c0392b", "#2e86de"])
for i, v in enumerate([680000, 11500]):
    ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=9)
ax.set_ylabel("Electric-bus stock 2024 (units)")
ax.set_title("Electric-bus fleet scale: China vs India (2024)\nSource: IEA Global EV Outlook 2025")
save(fig, "chart_china_vs_india_stock.png")

# 6 India public charging stations 2024
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(["India public\nEV charging\nstations (Dec 2024)"], [25202], color="#27ae60", width=0.5)
ax.text(0, 25202, "25,202", ha="center", va="bottom", fontsize=11)
ax.set_ylabel("Public charging stations")
ax.set_title("India public EV charging infrastructure\nSource: India MoHI / PM E-DRIVE (Rs 2,000 cr allocated)")
ax.set_ylim(0, 30000)
save(fig, "chart_india_charging_2024.png")

print("Done. Charts in", CHARTS)
