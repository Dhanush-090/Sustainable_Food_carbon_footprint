# ============================================================
# Sustainable Food Carbon Footprint Calculator
# ============================================================
# Tech Stack : Streamlit | Pandas | Plotly Express | Plotly GO
# Dataset    : Food_Production.csv  (same folder as app.py)
# No ML, No pickle, No external APIs
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Sustainable Food Carbon Footprint Calculator",
    page_icon="plant",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------
# CUSTOM CSS  -  Green-themed professional UI
# -------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #0d1f0f 0%, #0a1a0c 40%, #0f2310 100%);
        color: #e8f5e9;
    }
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #388e3c 100%);
        border-radius: 20px; padding: 2.5rem 3rem; margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(56,142,60,0.35);
        border: 1px solid rgba(129,199,132,0.25); text-align: center;
    }
    .main-header h1 { font-size: 2.8rem; font-weight: 800; color: #ffffff; margin: 0 0 0.4rem 0; }
    .main-header p  { font-size: 1.1rem; color: #c8e6c9; margin: 0; line-height: 1.6; }

    .section-title {
        font-size: 1.35rem; font-weight: 700; color: #81c784;
        margin: 2rem 0 1rem 0; border-left: 4px solid #4caf50; padding-left: 12px;
    }
    .metric-card {
        background: linear-gradient(145deg, #1b3a1d, #1e4620);
        border: 1px solid rgba(129,199,132,0.3); border-radius: 16px;
        padding: 1.5rem 1.2rem; text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4); height: 100%;
    }
    .metric-icon  { font-size: 2.2rem; margin-bottom: 0.5rem; }
    .metric-label { font-size: 0.82rem; color: #a5d6a7; font-weight: 600;
                    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.6rem; }
    .metric-value { font-size: 2rem; font-weight: 800; color: #ffffff; line-height: 1.1; }
    .metric-unit  { font-size: 0.78rem; color: #69f0ae; font-weight: 500; margin-top: 0.3rem; }
    .metric-category { font-size: 1.3rem; font-weight: 700; margin-top: 0.2rem; }

    .rec-box {
        background: linear-gradient(135deg, #1a3c1a, #1e4a20);
        border: 1px solid #4caf50; border-left: 5px solid #69f0ae;
        border-radius: 16px; padding: 1.8rem 2rem; margin: 1.2rem 0;
        box-shadow: 0 4px 24px rgba(76,175,80,0.2);
    }
    .rec-title { font-size: 1.1rem; font-weight: 700; color: #69f0ae; margin-bottom: 1rem; }
    .rec-grid  {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr));
        gap: 1rem; margin-top: 0.8rem;
    }
    .rec-item        { text-align: center; background: rgba(255,255,255,0.05);
                       border-radius: 10px; padding: 0.9rem 0.6rem; }
    .rec-item-label  { font-size: 0.75rem; color: #a5d6a7; text-transform: uppercase;
                       letter-spacing: 0.6px; margin-bottom: 0.4rem; }
    .rec-item-value  { font-size: 1.05rem; font-weight: 700; color: #ffffff; }
    .rec-reduction   { font-size: 1.6rem; font-weight: 800; color: #69f0ae; }

    .footer {
        text-align: center; color: #558b2f; font-size: 0.85rem;
        margin-top: 3rem; padding: 1.5rem;
        border-top: 1px solid rgba(129,199,132,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# CHART THEME
# -------------------------------------------------
PAPER_BG   = "rgba(27,58,29,0.6)"
FONT_COLOR = "#c8e6c9"
GRID_COLOR = "rgba(129,199,132,0.12)"
GREEN_SCALE = ["#1b5e20","#2e7d32","#388e3c","#43a047",
               "#4caf50","#66bb6a","#81c784","#a5d6a7","#c8e6c9"]

def apply_theme(fig):
    fig.update_layout(
        paper_bgcolor=PAPER_BG, plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=FONT_COLOR, size=13),
        margin=dict(t=60, b=40, l=40, r=40),
        legend=dict(bgcolor="rgba(0,0,0,0.3)",
                    bordercolor="rgba(129,199,132,0.3)",
                    borderwidth=1, font=dict(color=FONT_COLOR)),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
                     tickfont=dict(color=FONT_COLOR))
    fig.update_yaxes(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
                     tickfont=dict(color=FONT_COLOR))
    return fig

# -------------------------------------------------
# HELPER
# -------------------------------------------------
def get_category(val):
    if val < 5:
        return "🟢 Low Carbon"
    elif val <= 20:
        return "🟡 Medium Carbon"
    else:
        return "🔴 High Carbon"

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Food_Production.csv")
    df.columns = df.columns.str.strip()
    df.dropna(subset=["Food product", "Total_emissions"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

df = load_data()

COL_FOOD = "Food product"
COL_EMIT = "Total_emissions"
COL_WATER = "Freshwater withdrawals per kilogram (liters per kilogram)"
COL_LAND  = "Land use per kilogram (m\u00b2 per kilogram)"
BREAKDOWN = ["Land use change","Animal Feed","Farm","Processing","Transport","Packging","Retail"]

# ==================================================
# 1.  PAGE HEADER
# ==================================================
st.markdown(
    """
    <div class="main-header">
        <h1>\U0001f331 Sustainable Food Carbon Footprint Calculator</h1>
        <p>
            Every meal you choose carries a hidden environmental cost.
            Explore how your food choices impact <strong>carbon emissions</strong>,
            <strong>freshwater consumption</strong>, and <strong>land use</strong>&nbsp;&mdash;
            and discover greener alternatives for a healthier planet. \U0001f30d
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ==================================================
# 2.  FOOD SELECTION
# ==================================================
st.markdown('<p class="section-title">\U0001f957 Select a Food Product</p>', unsafe_allow_html=True)
food_list     = sorted(df[COL_FOOD].unique().tolist())
selected_food = st.selectbox("Choose a food product to analyse its environmental impact:",
                              options=food_list, key="food_sel")

food_row  = df[df[COL_FOOD] == selected_food].iloc[0]
emit_val  = float(food_row[COL_EMIT])
water_val = float(food_row[COL_WATER]) if COL_WATER in df.columns and pd.notna(food_row.get(COL_WATER)) else 0.0
land_val  = float(food_row[COL_LAND])  if COL_LAND  in df.columns and pd.notna(food_row.get(COL_LAND))  else 0.0
category  = get_category(emit_val)

# ==================================================
# 3.  IMPACT DASHBOARD  (4 metric cards)
# ==================================================
st.markdown('<p class="section-title">\U0001f4ca Environmental Impact Dashboard</p>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">\U0001f3ed</div>
        <div class="metric-label">Carbon Footprint</div>
        <div class="metric-value">{emit_val:.2f}</div>
        <div class="metric-unit">kg CO\u2082e / kg</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">\U0001f4a7</div>
        <div class="metric-label">Water Usage</div>
        <div class="metric-value">{water_val:,.1f}</div>
        <div class="metric-unit">L / kg</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">\U0001f33e</div>
        <div class="metric-label">Land Usage</div>
        <div class="metric-value">{land_val:.2f}</div>
        <div class="metric-unit">m\u00b2 / kg</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">\U0001f30d</div>
        <div class="metric-label">Environmental Category</div>
        <div class="metric-category">{category}</div>
    </div>""", unsafe_allow_html=True)

st.write("")

# ==================================================
# 4.  SUSTAINABLE ALTERNATIVE RECOMMENDATION
# ==================================================
st.markdown('<p class="section-title">\U0001f4a1 Sustainable Alternative Recommendation</p>', unsafe_allow_html=True)

alternatives = df[(df[COL_FOOD] != selected_food) & (df[COL_EMIT] < emit_val)].copy()

if alternatives.empty:
    st.info("\U0001f31f Great choice! This food already has one of the lowest carbon footprints in the dataset.")
else:
    alt_row   = alternatives.loc[alternatives[COL_EMIT].idxmax()]
    alt_name  = alt_row[COL_FOOD]
    alt_emit  = float(alt_row[COL_EMIT])
    reduction = ((emit_val - alt_emit) / emit_val) * 100

    st.markdown(f"""
    <div class="rec-box">
        <div class="rec-title">\u267b\ufe0f Switch to a Greener Option</div>
        <div class="rec-grid">
            <div class="rec-item">
                <div class="rec-item-label">Current Food</div>
                <div class="rec-item-value">\U0001f37d\ufe0f {selected_food}</div>
            </div>
            <div class="rec-item">
                <div class="rec-item-label">Recommended Alternative</div>
                <div class="rec-item-value">\U0001f33f {alt_name}</div>
            </div>
            <div class="rec-item">
                <div class="rec-item-label">Current Emissions</div>
                <div class="rec-item-value">{emit_val:.2f} kg CO\u2082e/kg</div>
            </div>
            <div class="rec-item">
                <div class="rec-item-label">Alternative Emissions</div>
                <div class="rec-item-value">{alt_emit:.2f} kg CO\u2082e/kg</div>
            </div>
            <div class="rec-item">
                <div class="rec-item-label">CO\u2082 Reduction</div>
                <div class="rec-reduction">\u2193 {reduction:.1f}%</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

st.write("")

# ==================================================
# 5.  EMISSION BREAKDOWN PIE CHART
# ==================================================
st.markdown('<p class="section-title">\U0001f967 Emission Sources Breakdown</p>', unsafe_allow_html=True)

b_labels, b_values = [], []
for col in BREAKDOWN:
    if col in df.columns:
        v = food_row.get(col, 0)
        if pd.notna(v) and float(v) > 0:
            b_labels.append(col)
            b_values.append(float(v))

if b_values:
    pie1 = go.Figure(go.Pie(
        labels=b_labels, values=b_values, hole=0.42,
        marker=dict(colors=GREEN_SCALE[:len(b_values)],
                    line=dict(color="#0d1f0f", width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#ffffff"),
        hovertemplate="<b>%{label}</b><br>%{value:.3f} kg CO\u2082e/kg<br>%{percent}<extra></extra>",
    ))
    pie1.update_layout(
        title=dict(text="Sources of Carbon Emissions for Selected Food",
                   font=dict(size=16, color=FONT_COLOR), x=0.5),
        annotations=[dict(text=f"<b>{emit_val:.2f}</b><br>kg CO\u2082e",
                          x=0.5, y=0.5, showarrow=False,
                          font=dict(size=14, color="#69f0ae"))],
    )
    pie1 = apply_theme(pie1)
    st.plotly_chart(pie1, use_container_width=True)
else:
    st.warning("\u26a0\ufe0f Breakdown data not available for this product.")

st.markdown("---")

# ==================================================
# 6.  FOOD COMPARISON  (grouped bar chart)
# ==================================================
st.markdown('<p class="section-title">\u2696\ufe0f Compare Two Foods</p>', unsafe_allow_html=True)

compare_opts = [f for f in food_list if f != selected_food]
compare_food = st.selectbox("Compare With:", options=compare_opts, key="cmp_sel")
cmp_row = df[df[COL_FOOD] == compare_food].iloc[0]

metrics_labels = ["Carbon Footprint (kg CO\u2082e/kg)", "Water Usage (L/kg)", "Land Usage (m\u00b2/kg)"]
vals1 = [emit_val, water_val, land_val]
vals2 = [
    float(cmp_row[COL_EMIT]),
    float(cmp_row[COL_WATER]) if COL_WATER in df.columns and pd.notna(cmp_row.get(COL_WATER)) else 0.0,
    float(cmp_row[COL_LAND])  if COL_LAND  in df.columns and pd.notna(cmp_row.get(COL_LAND))  else 0.0,
]

bar_cmp = go.Figure()
bar_cmp.add_trace(go.Bar(
    name=selected_food, x=metrics_labels, y=vals1,
    marker_color="#4caf50", marker_line=dict(color="#1b5e20", width=1.5),
    text=[f"{v:.2f}" for v in vals1], textposition="outside",
    textfont=dict(color="#c8e6c9", size=11),
))
bar_cmp.add_trace(go.Bar(
    name=compare_food, x=metrics_labels, y=vals2,
    marker_color="#81c784", marker_line=dict(color="#1b5e20", width=1.5),
    text=[f"{v:.2f}" for v in vals2], textposition="outside",
    textfont=dict(color="#c8e6c9", size=11),
))
bar_cmp.update_layout(
    barmode="group",
    title=dict(text=f"\U0001f50d {selected_food}  vs  {compare_food}",
               font=dict(size=16, color=FONT_COLOR), x=0.5),
    xaxis_title="Environmental Metric", yaxis_title="Value",
    bargap=0.25, bargroupgap=0.1,
)
bar_cmp = apply_theme(bar_cmp)
st.plotly_chart(bar_cmp, use_container_width=True)

st.markdown("---")

# ==================================================
# 7.  TOP 10 HIGHEST CARBON FOODS
# ==================================================
st.markdown('<p class="section-title">\U0001f51d Top 10 Highest Carbon Footprint Foods</p>', unsafe_allow_html=True)

top10 = df.nlargest(10, COL_EMIT)[[COL_FOOD, COL_EMIT]].sort_values(COL_EMIT, ascending=True)

bar_top = go.Figure(go.Bar(
    x=top10[COL_EMIT], y=top10[COL_FOOD], orientation="h",
    marker=dict(
        color=top10[COL_EMIT],
        colorscale=[[0,"#2e7d32"],[0.5,"#66bb6a"],[1,"#ff5252"]],
        showscale=True,
        colorbar=dict(title=dict(text="kg CO\u2082e/kg", font=dict(color=FONT_COLOR)),
                      tickfont=dict(color=FONT_COLOR)),
        line=dict(color="#0d1f0f", width=0.8),
    ),
    text=[f"{v:.2f} kg CO\u2082e/kg" for v in top10[COL_EMIT]],
    textposition="outside", textfont=dict(color="#c8e6c9", size=11),
    hovertemplate="<b>%{y}</b><br>%{x:.2f} kg CO\u2082e/kg<extra></extra>",
))
bar_top.update_layout(
    title=dict(text="\U0001f3ed Top 10 Foods by Carbon Footprint",
               font=dict(size=16, color=FONT_COLOR), x=0.5),
    xaxis_title="Total Emissions (kg CO\u2082e / kg)",
    yaxis_title="", height=450,
)
bar_top = apply_theme(bar_top)
st.plotly_chart(bar_top, use_container_width=True)

st.markdown("---")

# ==================================================
# 8.  SUSTAINABILITY CATEGORY DISTRIBUTION
# ==================================================
st.markdown('<p class="section-title">\U0001f4c8 Sustainability Category Distribution</p>', unsafe_allow_html=True)

df["_Category"] = df[COL_EMIT].apply(get_category)
cat_counts = df["_Category"].value_counts().reset_index()
cat_counts.columns = ["Category", "Count"]

cat_color_map = {
    "\U0001f7e2 Low Carbon":    "#4caf50",
    "\U0001f7e1 Medium Carbon": "#ffc107",
    "\U0001f534 High Carbon":   "#f44336",
}
colors = [cat_color_map.get(c, "#66bb6a") for c in cat_counts["Category"]]

pie2 = go.Figure(go.Pie(
    labels=cat_counts["Category"], values=cat_counts["Count"], hole=0.44,
    marker=dict(colors=colors, line=dict(color="#0d1f0f", width=2)),
    textinfo="label+percent+value",
    textfont=dict(size=12, color="#ffffff"),
    hovertemplate="<b>%{label}</b><br>%{value} foods (%{percent})<extra></extra>",
))
pie2.update_layout(
    title=dict(text="\U0001f30d Distribution of Foods by Carbon Category",
               font=dict(size=16, color=FONT_COLOR), x=0.5),
    annotations=[dict(text=f"<b>{len(df)}</b><br>foods",
                      x=0.5, y=0.5, showarrow=False,
                      font=dict(size=15, color="#69f0ae"))],
)
pie2 = apply_theme(pie2)
st.plotly_chart(pie2, use_container_width=True)

st.markdown("---")

# ==================================================
# 9.  DATA EXPLORER
# ==================================================
with st.expander("\U0001f4cb View Complete Dataset", expanded=False):
    st.markdown(
        f"<p style='color:#a5d6a7; margin-bottom:0.8rem;'>"
        f"Showing <strong>{len(df)}</strong> food products with their environmental metrics.</p>",
        unsafe_allow_html=True,
    )
    show_df = df.drop(columns=["_Category"], errors="ignore")
    st.dataframe(
        show_df.style.background_gradient(subset=[COL_EMIT], cmap="YlGn"),
        use_container_width=True, height=420,
    )

# ==================================================
# FOOTER
# ==================================================
st.markdown(
    """
    <div class="footer">
        \U0001f331 <strong>Sustainable Food Carbon Footprint Calculator</strong> &nbsp;|&nbsp;
        Built with Streamlit &amp; Plotly &nbsp;|&nbsp;
        Data: Food_Production.csv &nbsp;|&nbsp;
        \U0001f30d Make every meal count for the planet.
    </div>
    """,
    unsafe_allow_html=True,
)
