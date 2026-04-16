import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, time
st.write("🕒 Current Time (IST):", datetime.now().strftime("%I:%M:%S %p"))
st.set_page_config(page_title="Play Store Dashboard", layout="wide")

st.title("📊 Google Play Store Analytics Dashboard")

try:
    apps_df = pd.read_excel("cleaned_apps1.xlsx")
    reviews_df = pd.read_excel("cleaned_reviews.xlsx")
except Exception as e:
    st.error(f"Error loading files: {e}")

merged_df = pd.merge(apps_df, reviews_df, on="App", how="inner")

merged_df["Installs"] = merged_df["Installs"].astype(str).str.replace("[+,]", "", regex=True)
merged_df["Installs"] = pd.to_numeric(merged_df["Installs"], errors="coerce")

merged_df["Reviews"] = pd.to_numeric(merged_df["Reviews"], errors="coerce")

merged_df["Size"] = merged_df["Size"].astype(str)


st.sidebar.header("🔍 Filters")

category_options = merged_df["Category"].dropna().unique().tolist()

selected_categories = st.sidebar.multiselect(
    "Select Category",
    category_options,
    default=category_options
)

rating_range = st.sidebar.slider(
    "Rating Range",
    0.0, 5.0,
    (3.5, 5.0)
)

min_installs = st.sidebar.number_input("Minimum Installs", value=0)
min_reviews = st.sidebar.number_input("Minimum Reviews", value=0)

df_global = merged_df[
    (merged_df["Category"].isin(selected_categories)) &
    (merged_df["Rating"].between(rating_range[0], rating_range[1])) &
    (merged_df["Installs"] >= min_installs) &
    (merged_df["Reviews"] >= min_reviews)
].copy()


categories = [
    "GAME", "BEAUTY", "BUSINESS", "COMICS",
    "COMMUNICATION", "DATING", "ENTERTAINMENT",
    "SOCIAL", "EVENTS"
]

def show_task(fig, title, start, end, key):
    st.subheader(title)

    # TEMP FIX
    if True:
        st.plotly_chart(fig, use_container_width=True, key=key)
    else:
        st.warning(f"⛔ Available only between {start} and {end}")

#def show_task(fig, title, start, end, key):
#   st.subheader(title)
 #   current_time = datetime.now().time()

#    if start <= current_time <= end:
 #       st.plotly_chart(fig, use_container_width=True, key=key)
  #  else:
   #     st.info(f"""
    #    ⏳ This visualization is time-restricted  
#
 #       **Available between:** {start.strftime('%I:%M %p')} – {end.strftime('%I:%M %p')} IST  

  #      Please revisit during the active time window.
        """)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Bubble",
    "Map",
    "Trend",
    "Area",
    "Bar",
    "Revenue"
])


# TASK 1 - BUBBLE CHART

df1 = df_global[
    (df_global["Rating"] > 3.5) &
    (df_global["Category"].isin(categories)) &
    (df_global["Reviews"] > 500) &
    (~df_global["App"].str.contains("S", case=False, na=False)) &
    (df_global["Sentiment_Subjectivity"] > 0.5) &
    (df_global["Installs"] > 50000)
].copy()

df1["Category"] = df1["Category"].replace({
    "BEAUTY": "सौंदर्य",
    "BUSINESS": "வணிகம்",
    "DATING": "Dating (Deutsch)"
})

fig1 = px.scatter(
    df1,
    x="Size",
    y="Rating",
    size="Installs",
    color="Category",
    hover_name="App",
    title="Bubble Chart: Size vs Rating"
)

fig1.update_traces(marker=dict(line=dict(width=1, color="white")))
fig1.update_traces(
    selector=dict(name="GAME"),
    marker=dict(color="pink", line=dict(width=1, color="white"))
)

with tab1:
    show_task(fig1, "Task 1: Bubble Chart", time(17, 0), time(19, 0), "t1")


# TASK 2 - CHOROPLETH

df2 = df_global.copy()

df2["Installs"] = pd.to_numeric(df2["Installs"], errors="coerce")
df2 = df2[~df2["Category"].str.startswith(("A", "C", "G", "S"), na=False)]

grouped2 = df2.groupby("Category")["Installs"].sum().reset_index()
top5 = grouped2.nlargest(5, "Installs")

countries = ["India", "United States", "Germany", "France", "Brazil"]
top5["Country"] = countries[:len(top5)]

fig2 = px.choropleth(
    top5,
    locations="Country",
    locationmode="country names",
    color="Installs",
    hover_name="Category",
    title="Global Installs by Category"
)

with tab2:
    show_task(fig2, "Task 2: Choropleth Map", time(18, 0), time(20, 0), "t2")


# TASK 3 - TIME SERIES

df3 = df_global.copy()

df3["Last Updated"] = pd.to_datetime(df3["Last Updated"], errors="coerce")
df3["YearMonth"] = df3["Last Updated"].dt.to_period("M").astype(str)

df3 = df3[
    (~df3["App"].str.startswith(("X","Y","Z"), na=False)) &
    (~df3["App"].str.contains("S", case=False, na=False)) &
    (df3["Category"].str.startswith(("E","C","B"), na=False)) &
    (df3["Reviews"] > 500)
].copy()

grouped3 = df3.groupby(["YearMonth", "Category"])["Installs"].sum().reset_index()

fig3 = px.line(
    grouped3,
    x="YearMonth",
    y="Installs",
    color="Category",
    title="Time Series Install Trend"
)

with tab3:
    show_task(fig3, "Task 3: Time Series", time(18, 0), time(21, 0), "t3")


# TASK 4 - AREA CHART

df4 = df_global.copy()
df4 = df4[~df4["App"].str.contains(r"\d", na=False)]

df4["Month"] = pd.to_datetime(df4["Last Updated"], errors="coerce").dt.to_period("M").astype(str)

grouped4 = df4.groupby(["Month", "Category"])["Installs"].sum().reset_index()

fig4 = px.area(
    grouped4,
    x="Month",
    y="Installs",
    color="Category",
    title="Cumulative Installs Over Time"
)

with tab4:
    show_task(fig4, "Task 4: Area Chart", time(16, 0), time(18, 0), "t4")


# TASK 5 - BAR CHART

df5 = df_global.copy()
df5["Month"] = pd.to_datetime(df5["Last Updated"], errors="coerce").dt.month
df5 = df5[df5["Month"] == 1]

grouped5 = df5.groupby("Category").agg({
    "Rating": "mean",
    "Reviews": "sum"
}).reset_index()

top10 = grouped5.nlargest(10, "Reviews")

fig5 = go.Figure()

fig5.add_trace(go.Bar(
    x=top10["Category"],
    y=top10["Rating"],
    name="Rating",
    marker=dict(color="skyblue"),
    text=top10["Rating"],
    textposition="outside",
    yaxis="y1"
))

fig5.add_trace(go.Bar(
    x=top10["Category"],
    y=top10["Reviews"],
    name="Reviews"
))

fig5.update_layout(
    barmode='group',
    title='Rating vs Reviews',
    yaxis=dict(title='Average Rating', range=[0, 5]),
    yaxis2=dict(title='Total Reviews', overlaying='y', side='right')
)

with tab5:
    show_task(fig5, "Task 5: Bar Chart", time(15, 0), time(17, 0), "t5")


# TASK 6 - FREE VS PAID

df6 = df_global.copy()

df6["Installs"] = pd.to_numeric(df6["Installs"], errors="coerce")
df6["Price"] = pd.to_numeric(df6["Price"], errors="coerce")
df6["Revenue"] = df6["Price"] * df6["Installs"]

df6 = df6[df6["Installs"] > 10000]

grouped6 = df6.groupby("Type").agg({
    "Installs": "mean",
    "Revenue": "mean"
}).reset_index()

fig6 = go.Figure()

fig6.add_trace(go.Bar(
    x=grouped6["Type"],
    y=grouped6["Installs"],
    name="Installs"
))

fig6.add_trace(go.Scatter(
    x=grouped6["Type"],
    y=grouped6["Revenue"],
    name="Revenue",
    yaxis="y2"
))

fig6.update_layout(
    title="Free vs Paid Apps",
    yaxis2=dict(overlaying="y", side="right")
)

with tab6:
    show_task(fig6, "Task 6: Free vs Paid", time(13, 0), time(14, 0), "t6")