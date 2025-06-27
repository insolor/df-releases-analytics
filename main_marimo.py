import marimo

__generated_with = "0.14.8"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    from datetime import datetime
    import altair as alt
    import pandas as pd
    return alt, datetime, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Dwarf Fortress releases analytics

    Based on data from
    [bay12games.com/dwarves/older_versions](https://bay12games.com/dwarves/older_versions.html) and
    information about betas from [steam](https://store.steampowered.com/news/app/975370?updates=true).
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    checkbox = mo.ui.checkbox(label="Add betas")
    checkbox
    return (checkbox,)


@app.cell(hide_code=True)
def _(checkbox, pd):
    df = pd.read_csv("releases.csv")

    date_column = "release_date"

    # Add beta versions
    betas = pd.read_json("betas.json")

    if checkbox.value:
        df = pd.concat([df, betas])
        df.sort_values(by=[date_column], inplace=True, ignore_index=True)

    df[date_column] = pd.to_datetime(df[date_column])
    # df
    return date_column, df


@app.cell(hide_code=True)
def _(mo):
    group_by = mo.ui.radio(label="Group by", options=["Months", "Quarters", "Years"], value="Quarters")
    group_by
    return (group_by,)


@app.cell(hide_code=True)
def _(group_by):
    match group_by.value:
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
    return axis_name, period_letter, period_name


@app.cell(hide_code=True)
def _(date_column, datetime, df, pd, period_letter):
    start_date = df[date_column].min().to_period(period_letter)
    end_date = pd.Period(datetime.now(), period_letter)

    period_range = pd.period_range(start=start_date, end=end_date, freq=period_letter)

    df["bucket"] = df[date_column].dt.to_period(period_letter)
    df["version_with_date"] = df.apply(lambda row: (row["name"], row["release_date"].date().isoformat()), axis=1)

    buckets = df.groupby("bucket").agg({"version_with_date": lambda x: list(x)}).reindex(period_range, fill_value=[])

    buckets.index = buckets.index.astype(str)
    buckets["count"] = buckets["version_with_date"].apply(len)
    return (buckets,)


@app.function(hide_code=True)
def format_version_with_date(versions_with_dates: list[tuple[str, str]]) -> str:
    return ", ".join([f"{version} ({day})" for version, day in versions_with_dates])


@app.cell(hide_code=True)
def _(alt, axis_name, buckets, period_name):
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
    return (chart,)


@app.cell(hide_code=True)
def _(chart, mo):
    altair_chart = mo.ui.altair_chart(chart)
    altair_chart
    return (altair_chart,)


@app.cell(hide_code=True)
def _(altair_chart, buckets, mo, pd):
    selection = list(altair_chart.selections.values())

    if selection and selection[0].get("bucket"):
        bucket = selection[0]["bucket"]

        if len(bucket) == 1:
            mo.output.append(f"Selected period: {bucket[0]}")
        else:
            mo.output.append(f"Selected period: from {bucket[0]} to {bucket[-1]}")

        versions_with_dates = (
            buckets.loc[bucket[0] : bucket[-1]]["version_with_date"].apply(pd.Series).stack().unique().tolist()
        )

        selected_df = pd.DataFrame(versions_with_dates, columns=["version", "date"])
        mo.output.append(selected_df)
    return


if __name__ == "__main__":
    app.run()
