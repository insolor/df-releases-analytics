import streamlit as st

import pandas as pd
import altair as alt


def show_calendar():
    # Define the date range for the calendar
    start_date = "2024-01-01"
    end_date = "2024-03-31"

    # Create a complete grid of dates
    calendar = pd.DataFrame({"date": pd.date_range(start=start_date, end=end_date)})

    # Add necessary columns for calendar layout
    calendar["day_of_week"] = calendar["date"].dt.dayofweek  # Monday=0, Sunday=6
    calendar["week_of_year"] = calendar["date"].dt.isocalendar().week
    calendar["month"] = calendar["date"].dt.month

    # Release days with versions
    release_data = pd.DataFrame(
        {"date": pd.to_datetime(["2024-01-10", "2024-01-20", "2024-02-05"]), "version": ["v1", "v2", "v3"]}
    )

    # Merge release data with the full calendar
    calendar = calendar.merge(release_data, on="date", how="left")

    # Create the calendar chart
    chart = (
        alt.Chart(calendar)
        .mark_rect(size=30)
        .encode(
            y=alt.Y("day_of_week:O", title="Day of Week", sort=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
            x=alt.X("week_of_year:O", title="Week of Year"),
            color=alt.Color("version:N", title="Version", scale=alt.Scale(scheme="category10")),
            tooltip=[alt.Tooltip("date:T", title="Date"), alt.Tooltip("version:N", title="Version")],
        )
        .properties(
            width=400,
            height=300,
        )
        .configure_axis(labelFontSize=12, titleFontSize=14)
    )

    st.altair_chart(chart, use_container_width=True)


show_calendar()
