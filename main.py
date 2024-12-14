import altair as alt
import pandas as pd
import streamlit as st

title = "Dwarf Fortress releases analytics"
st.set_page_config(page_title=title, layout="wide", page_icon="📈")

st.header(title)

df = pd.read_csv("releases.csv")

date_column = "release_date"

# Add 51.01 beta versions
betas = pd.read_csv("betas.csv")
df = pd.concat([df, betas])
df.sort_values(by=[date_column], inplace=True, ignore_index=True)

df[date_column] = pd.to_datetime(df[date_column])

start_date = df[date_column].min().to_period("M")
end_date = df[date_column].max().to_period("M")
all_months = pd.period_range(start=start_date, end=end_date, freq="M")

df["bucket"] = df[date_column].dt.to_period("M")
df["version_with_date"] = df.apply(
    lambda row: (row["version_number"], row["release_date"].date().isoformat()), axis=1
)

buckets = (
    df.groupby("bucket")
    .agg({"version_with_date": lambda x: list(x)})
    .reindex(all_months, fill_value=[])
)

buckets.index = buckets.index.astype(str)
buckets["count"] = buckets["version_with_date"].apply(len)


def format_version_with_date(versions_with_dates: list[tuple[str, str]]) -> str:
    return ", ".join([f"{version} ({day})" for version, day in versions_with_dates])


buckets["versions"] = buckets["version_with_date"].apply(
    format_version_with_date
)

interval = alt.selection_interval(encodings=["x"])

chart_data = buckets.reset_index().rename(columns={"index": "bucket"})
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("bucket:O", title="Month"),
        y=alt.Y("count:Q", title="Count"),
        tooltip=[
            alt.Tooltip("bucket:O", title="Month"),
            alt.Tooltip("count:Q", title="Count"),
            alt.Tooltip("versions:N", title="Releases"),
        ],
    )
    .properties(
        title="Count of releases",
        height=300,
    )
    .add_params(interval)
)

event = st.altair_chart(chart, use_container_width=True, on_select="rerun")

selection = event["selection"]["param_1"]
if selection:
    bucket = selection["bucket"]
    versions_with_dates = (
        buckets.loc[bucket[0] : bucket[-1]]["version_with_date"]
        .apply(pd.Series)
        .stack()
        .unique()
    ).tolist()
    
    df = pd.DataFrame(versions_with_dates, columns=['version', 'date'])
    st.table(df)
