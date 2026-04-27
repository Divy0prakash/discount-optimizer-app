
# streamlit_app.py
# pip install streamlit plotly pandas
# streamlit run streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib

st.set_page_config(page_title="DTI — Discount Optimizer", page_icon="🛍️", layout="wide")
st.title("🛍️ DTI — Dynamic Discount Optimizer")
st.caption("Optimizing product discounts using review sentiments & price sensitivity")

@st.cache_data
def load_data():
    recs    = pd.read_csv("top_recommendations.csv")
    unified = pd.read_csv("unified_dataset.csv")
    return recs, unified

recs, unified = load_data()

st.sidebar.header("🎛️ Filters")
seasons  = ["All"] + sorted(unified["season"].dropna().unique().tolist())
season   = st.sidebar.selectbox("Season", seasons)
festival = st.sidebar.checkbox("Festival period only", value=False)
top_n    = st.sidebar.slider("Top N products", 5, 20, 10)
min_sent = st.sidebar.slider("Min Sentiment", -1.0, 1.0, -1.0, 0.1)

df = recs.copy()
if season != "All":  df = df[df["season"] == season]
if festival:         df = df[df["festival"] == 1]
df = df[df["sentiment_score"] >= min_sent].head(top_n)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Products Shown",  len(df))
c2.metric("Avg Sentiment",   f"{df.get('sentiment_score',  pd.Series([0])).mean():.2f}")
c3.metric("Avg Discount",    f"{df.get('recommended_discount_pct', pd.Series([0])).mean():.1f}%")
c4.metric("Avg Eff. Price",  f"${df.get('effective_price', pd.Series([0])).mean():.2f}")

st.divider()
st.subheader("📋 Recommendations")
show = [c for c in ["product_id","category","price","effective_price",
         "recommended_discount_pct","sentiment_score","pop_score"] if c in df.columns]
st.dataframe(df[show].style
    .format({"price":"${:.2f}","effective_price":"${:.2f}",
              "recommended_discount_pct":"{:.0f}%",
              "sentiment_score":"{:.3f}","pop_score":"{:.4f}"})
    .background_gradient(subset=["recommended_discount_pct"], cmap="YlOrRd")
    .background_gradient(subset=["sentiment_score"],          cmap="RdYlGn"),
    use_container_width=True)

col_l, col_r = st.columns(2)
with col_l:
    fig1 = px.bar(df, x="product_id", y="recommended_discount_pct",
                   color="sentiment_score", color_continuous_scale="RdYlGn",
                   title="Recommended Discount by Product")
    st.plotly_chart(fig1, use_container_width=True)
with col_r:
    fig2 = px.scatter(df, x="price", y="sentiment_score",
                       size="recommended_discount_pct", color="pop_score",
                       hover_data=["product_id","category"],
                       title="Price vs Sentiment  (size = discount)",
                       color_continuous_scale="Viridis")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("📅 Seasonality")
col1, col2 = st.columns(2)
with col1:
    s_df = unified.groupby("season")["units_sold"].sum().reset_index()
    st.plotly_chart(px.bar(s_df, x="season", y="units_sold",
                            color="season", title="Units Sold by Season"),
                    use_container_width=True)
with col2:
    f_df = unified.groupby("festival")["units_sold"].mean().reset_index()
    f_df["period"] = f_df["festival"].map({0:"Non-Festival", 1:"Festival"})
    st.plotly_chart(px.pie(f_df, names="period", values="units_sold",
                            title="Sales: Festival vs Normal",
                            color_discrete_sequence=["#4CAF50","#FF7043"]),
                    use_container_width=True)
