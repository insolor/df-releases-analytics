import altair as alt
import pandas as pd
import streamlit as st

title = "Dwarf Fortress releases analytics"
st.set_page_config(page_title=title, layout="wide", page_icon="📈")

st.header(title)

st.markdown("""Based on data from
[bay12games.com/dwarves/older_versions](https://bay12games.com/dwarves/older_versions.html) and
information about betas from [steam](https://store.steampowered.com/news/app/975370?updates=true).
""")

df = pd.read_csv("releases.csv")

date_column = "release_date"

# Add beta versions
betas = pd.read_json("betas.json")
if st.checkbox("Add betas"):
    df = pd.concat([df, betas])
    df.sort_values(by=[date_column], inplace=True, ignore_index=True)

df[date_column] = pd.to_datetime(df[date_column])

group_by = st.radio("Group by", ["Months", "Quarters", "Years"])
match group_by:
    case "Months":
        period_letter = "M"
        period_name = "Month"
        axis_name = "Months"
    case "Quarters":
        period_letter = "Q"
        period_name = "Quarter"
        axis_name = "Quarters"
    case "Years":
        period_letter = "Y"
        period_name = "Year"
        axis_name = "Years"

start_date = df[date_column].min().to_period(period_letter)
end_date = df[date_column].max().to_period(period_letter)
period_range = pd.period_range(start=start_date, end=end_date, freq=period_letter)

df["bucket"] = df[date_column].dt.to_period(period_letter)
df["version_with_date"] = df.apply(lambda row: (row["version_number"], row["release_date"].date().isoformat()), axis=1)

buckets = df.groupby("bucket").agg({"version_with_date": lambda x: list(x)}).reindex(period_range, fill_value=[])

buckets.index = buckets.index.astype(str)
buckets["count"] = buckets["version_with_date"].apply(len)


def format_version_with_date(versions_with_dates: list[tuple[str, str]]) -> str:
    return ", ".join([f"{version} ({day})" for version, day in versions_with_dates])


buckets["versions"] = buckets["version_with_date"].apply(format_version_with_date)

interval = alt.selection_interval(encodings=["x"])

chart_data = buckets.reset_index().rename(columns={"index": "bucket"})
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("bucket:O", title=axis_name),
        y=alt.Y("count:Q", title="Count"),
        tooltip=[
            alt.Tooltip("bucket:O", title=period_name),
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

    if len(bucket) == 1:
        st.write(f"Selected period: {bucket[0]}")
    else:
        st.write(f"Selected period: from {bucket[0]} to {bucket[-1]}")

    versions_with_dates = (
        buckets.loc[bucket[0] : bucket[-1]]["version_with_date"].apply(pd.Series).stack().unique()
    ).tolist()

    df = pd.DataFrame(versions_with_dates, columns=["version", "date"])
    st.dataframe(df, hide_index=True, width=500)
