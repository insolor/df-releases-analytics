import altair as alt
import pandas as pd
import streamlit as st

df = pd.read_csv("releases.csv")
# st.write(df)

date_column = "release_date"

df[date_column] = pd.to_datetime(df[date_column])

start_date = df[date_column].min().to_period("Q")
end_date = df[date_column].max().to_period("Q")
all_months = pd.period_range(start=start_date, end=end_date, freq="Q")

df["quarter"] = df[date_column].dt.to_period("Q")
df["version_with_date"] = df.apply(lambda row: f"{row["version_number"]} ({row["release_date"].date()})", axis=1)

monthly_counts = df.groupby("quarter").agg({
    "version_with_date": lambda x: list(x)
}).reindex(all_months, fill_value=[])

monthly_counts.index = monthly_counts.index.astype(str)
monthly_counts["count"] = monthly_counts["version_with_date"].apply(len)
monthly_counts["versions"] = monthly_counts["version_with_date"].apply(", ".join)

# st.write(monthly_counts)

chart_data = monthly_counts.reset_index().rename(columns={"index": "quarter"})
chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X("quarter:O", title="Quarter"),
    y=alt.Y("count:Q", title="Count"),
    tooltip=[
        alt.Tooltip("quarter:O", title="Quarter"),
        # alt.Tooltip("count:Q", title="Count"),
        alt.Tooltip("versions:N", title="Releases")
    ]
).properties(
    title="Count of releases per quarter",
    # width=700,
    height=300,
)

st.header("Dwar Fortress releases per quarter")
st.altair_chart(chart, use_container_width=True)
