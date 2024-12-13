import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dwarf Fortress releases per quarter", layout="wide")

st.header("Dwarf Fortress releases per quarter")

df = pd.read_csv("releases.csv")

date_column = "release_date"

# Add 51.01 beta versions
betas = pd.read_csv("betas.csv")
df = pd.concat([df, betas])
df.sort_values(by=[date_column], inplace=True, ignore_index=True)

df[date_column] = pd.to_datetime(df[date_column])

start_date = df[date_column].min().to_period("Q")
end_date = df[date_column].max().to_period("Q")
all_months = pd.period_range(start=start_date, end=end_date, freq="Q")

df["quarter"] = df[date_column].dt.to_period("Q")
df["version_with_date"] = df.apply(
    lambda row: (row["version_number"], row["release_date"].date().isoformat()), axis=1
)

quarterly_counts = (
    df.groupby("quarter")
    .agg({"version_with_date": lambda x: list(x)})
    .reindex(all_months, fill_value=[])
)

quarterly_counts.index = quarterly_counts.index.astype(str)
quarterly_counts["count"] = quarterly_counts["version_with_date"].apply(len)


def format_version_with_date(versions_with_dates: list[tuple[str, str]]) -> str:
    return ", ".join([f"{version} ({day})" for version, day in versions_with_dates])


quarterly_counts["versions"] = quarterly_counts["version_with_date"].apply(
    format_version_with_date
)

interval = alt.selection_interval(encodings=["x"])

chart_data = quarterly_counts.reset_index().rename(columns={"index": "quarter"})
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("quarter:O", title="Quarter"),
        y=alt.Y("count:Q", title="Count"),
        tooltip=[
            alt.Tooltip("quarter:O", title="Quarter"),
            alt.Tooltip("count:Q", title="Count"),
            alt.Tooltip("versions:N", title="Releases"),
        ],
    )
    .properties(
        title="Count of releases per quarter",
        height=300,
    )
    .add_params(interval)
)

event = st.altair_chart(chart, use_container_width=True, on_select="rerun")

selection = event["selection"]["param_1"]
if selection:
    quarters = selection["quarter"]
    versions_with_dates = (
        quarterly_counts.loc[quarters[0] : quarters[-1]]["version_with_date"]
        .apply(pd.Series)
        .stack()
        .unique()
    ).tolist()
    
    df = pd.DataFrame(versions_with_dates, columns=['version', 'date'])
    st.write(df)
