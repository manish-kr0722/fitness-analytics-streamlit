from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
WEEKDAYS = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
ACTIVITY_ORDER = ["Sedentary", "Lightly Active", "Fairly Active", "Very Active"]
SLEEP_ORDER = [
    "Less than 6 hours", "6 to less than 7 hours",
    "7 to 9 hours", "More than 9 hours",
]
COLORS = {
    "navy": "#17324D",
    "teal": "#168C8C",
    "orange": "#FC4C02",
    "blue": "#4C78A8",
    "gold": "#D9A441",
    "slate": "#73879C",
    "light": "#EAF1F6",
}


st.set_page_config(
    page_title="Fitness Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background: #F4F7FA; }
    [data-testid="stSidebar"] { background: #17324D; }
    [data-testid="stSidebar"] * { color: #FFFFFF; }
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DCE6EE;
        border-radius: 14px;
        padding: 15px 16px;
        box-shadow: 0 3px 12px rgba(23, 50, 77, 0.06);
    }
    .page-title {
        color: #17324D;
        font-size: 2.05rem;
        font-weight: 750;
        margin: 0 0 0.2rem 0;
    }
    .page-subtitle { color: #5F7285; margin-bottom: 1.3rem; }
    .section-title {
        color: #17324D;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1rem;
    }
    .insight-card {
        background: #FFFFFF;
        border-left: 5px solid #168C8C;
        border-radius: 12px;
        padding: 1rem 1.15rem;
        margin: 0.6rem 0;
        box-shadow: 0 3px 12px rgba(23, 50, 77, 0.05);
    }
    .note-card {
        background: #FFF7F2;
        border: 1px solid #FFD8C5;
        border-radius: 12px;
        padding: 1rem 1.15rem;
    }
    div[data-testid="stPlotlyChart"] {
        background: #FFFFFF;
        border: 1px solid #DCE6EE;
        border-radius: 14px;
        padding: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = pd.read_csv(DATA_DIR / "daily_fitness_master.csv", parse_dates=["ActivityDate"])
    hourly = pd.read_csv(
        DATA_DIR / "hourly_activity_master.csv",
        parse_dates=["ActivityHour", "ActivityDate"],
    )
    daily["IdLabel"] = daily["Id"].astype(str)
    hourly["IdLabel"] = hourly["Id"].astype(str)
    daily["DayName"] = pd.Categorical(daily["DayName"], WEEKDAYS, ordered=True)
    hourly["DayName"] = pd.Categorical(hourly["DayName"], WEEKDAYS, ordered=True)
    daily["ActivityLevel"] = pd.Categorical(daily["ActivityLevel"], ACTIVITY_ORDER, ordered=True)
    return daily, hourly


def page_heading(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def chart_title(number: int, title: str) -> None:
    st.markdown(f'<div class="section-title">{number}. {title}</div>', unsafe_allow_html=True)


def style_figure(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=35, r=25, t=55, b=40),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color=COLORS["navy"], size=12),
        title_font=dict(size=17, color=COLORS["navy"]),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#FFFFFF", font_color=COLORS["navy"]),
    )
    fig.update_xaxes(showgrid=False, linecolor="#CBD7E2")
    fig.update_yaxes(gridcolor="#E8EEF3", zeroline=False)
    return fig


def show_chart(fig: go.Figure) -> None:
    st.plotly_chart(style_figure(fig), use_container_width=True, config={"displaylogo": False})


def dataframe_csv(frame: pd.DataFrame) -> bytes:
    return frame.to_csv(index=False).encode("utf-8")


daily_all, hourly_all = load_data()

with st.sidebar:
    st.markdown("## Fitness Analytics")
    st.caption("Bellabeat / Fitbit case study")
    page = st.radio(
        "Dashboard page",
        [
            "Executive Overview",
            "Activity Analysis",
            "Sleep & Recovery",
            "Hourly & Heart Rate",
            "Insights & Data Quality",
        ],
    )
    st.markdown("---")
    st.markdown("### Global filters")
    min_date = daily_all["ActivityDate"].min().date()
    max_date = daily_all["ActivityDate"].max().date()
    selected_dates = st.date_input(
        "Activity date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    all_ids = sorted(daily_all["IdLabel"].unique().tolist())
    selected_ids = st.multiselect("Participants", all_ids, default=all_ids)
    selected_days = st.multiselect("Days of week", WEEKDAYS, default=WEEKDAYS)
    valid_only = st.toggle("Exclude possible non-wear days", value=True)
    st.caption("Filters apply to every page and download.")

date_start = pd.Timestamp(start_date)
date_end = pd.Timestamp(end_date)
daily = daily_all.loc[
    daily_all["ActivityDate"].between(date_start, date_end)
    & daily_all["IdLabel"].isin(selected_ids)
    & daily_all["DayName"].astype(str).isin(selected_days)
].copy()
if valid_only:
    daily = daily.loc[daily["PossibleNonWearDay"] == 0].copy()

hourly = hourly_all.loc[
    hourly_all["ActivityDate"].between(date_start, date_end)
    & hourly_all["IdLabel"].isin(selected_ids)
    & hourly_all["DayName"].astype(str).isin(selected_days)
].copy()

if daily.empty:
    st.warning("No daily records match the current filters. Change the sidebar selections.")
    st.stop()

sleep = daily.dropna(subset=["TotalMinutesAsleep"]).copy()


if page == "Executive Overview":
    page_heading(
        "Executive Overview",
        "Daily activity, goal achievement, energy use, and sleep coverage for the selected population.",
    )
    sleep_hours = sleep["SleepHours"].mean() if not sleep.empty else np.nan
    kpi_values = [
        ("Participants", f"{daily['Id'].nunique():,}"),
        ("Valid activity days", f"{len(daily):,}"),
        ("Average daily steps", f"{daily['TotalSteps'].mean():,.0f}"),
        ("10k goal achievement", f"{daily['Met10000StepGoal'].mean():.1%}"),
        ("Average calories", f"{daily['Calories'].mean():,.0f}"),
        ("Average sleep", "n.a." if np.isnan(sleep_hours) else f"{sleep_hours:.2f} h"),
    ]
    cols = st.columns(6)
    for col, (label, value) in zip(cols, kpi_values):
        col.metric(label, value)

    c1, c2 = st.columns(2)
    with c1:
        chart_title(1, "Average steps by weekday")
        weekday_steps = (
            daily.groupby("DayName", observed=False)["TotalSteps"].mean().reindex(WEEKDAYS).dropna().reset_index()
        )
        fig = px.bar(
            weekday_steps, x="DayName", y="TotalSteps",
            color_discrete_sequence=[COLORS["orange"]],
            labels={"DayName": "Day", "TotalSteps": "Average steps"},
            title="Weekly movement pattern",
        )
        show_chart(fig)

    with c2:
        chart_title(2, "Activity-level distribution")
        activity_counts = (
            daily["ActivityLevel"].value_counts().reindex(ACTIVITY_ORDER, fill_value=0).rename_axis("ActivityLevel").reset_index(name="Days")
        )
        fig = px.bar(
            activity_counts, x="ActivityLevel", y="Days", color="ActivityLevel",
            category_orders={"ActivityLevel": ACTIVITY_ORDER},
            color_discrete_sequence=[COLORS["slate"], COLORS["blue"], COLORS["teal"], COLORS["orange"]],
            labels={"ActivityLevel": "Activity level"},
            title="Participant-days by step category",
        )
        fig.update_layout(showlegend=False)
        show_chart(fig)

    c3, c4 = st.columns(2)
    with c3:
        chart_title(3, "Average minutes by activity category")
        minute_cols = ["VeryActiveMinutes", "FairlyActiveMinutes", "LightlyActiveMinutes", "SedentaryMinutes"]
        activity_minutes = (
            daily[minute_cols].mean().rename_axis("Category").reset_index(name="AverageMinutes")
        )
        activity_minutes["Category"] = activity_minutes["Category"].replace({
            "VeryActiveMinutes": "Very active",
            "FairlyActiveMinutes": "Fairly active",
            "LightlyActiveMinutes": "Lightly active",
            "SedentaryMinutes": "Sedentary",
        })
        fig = px.bar(
            activity_minutes, x="Category", y="AverageMinutes",
            color_discrete_sequence=[COLORS["teal"]],
            labels={"AverageMinutes": "Average minutes"},
            title="Daily time allocation",
        )
        show_chart(fig)

    with c4:
        chart_title(4, "Daily steps versus calories")
        corr = daily["TotalSteps"].corr(daily["Calories"])
        fig = px.scatter(
            daily, x="TotalSteps", y="Calories", trendline="ols",
            opacity=0.55, color_discrete_sequence=[COLORS["orange"]],
            labels={"TotalSteps": "Daily steps", "Calories": "Calories"},
            title=f"Steps and calories (correlation {corr:.2f})",
            hover_data=["IdLabel", "ActivityDate"],
        )
        show_chart(fig)


elif page == "Activity Analysis":
    page_heading(
        "Activity Analysis",
        "Sedentary time, calories, active minutes, distance, and daily distributions.",
    )
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Average active minutes", f"{daily['TotalActiveMinutes'].mean():.0f}")
    k2.metric("Average sedentary minutes", f"{daily['SedentaryMinutes'].mean():.0f}")
    k3.metric("Average distance", f"{daily['TotalDistance'].mean():.2f}")
    k4.metric("10k-step days", f"{daily['Met10000StepGoal'].sum():,}")

    chart_title(5, "Average sedentary minutes by participant")
    sedentary_by_id = (
        daily.groupby("IdLabel", as_index=False)["SedentaryMinutes"].mean().sort_values("SedentaryMinutes", ascending=True)
    )
    fig = px.bar(
        sedentary_by_id, x="SedentaryMinutes", y="IdLabel", orientation="h",
        color_discrete_sequence=[COLORS["slate"]],
        labels={"IdLabel": "Participant", "SedentaryMinutes": "Average sedentary minutes"},
        title="Sedentary time by participant",
    )
    show_chart(fig)

    c1, c2 = st.columns(2)
    with c1:
        chart_title(6, "Average calories by weekday")
        grouped = daily.groupby("DayName", observed=False)["Calories"].mean().reindex(WEEKDAYS).dropna().reset_index()
        fig = px.bar(grouped, x="DayName", y="Calories", color_discrete_sequence=[COLORS["gold"]], title="Daily energy use")
        show_chart(fig)
    with c2:
        chart_title(7, "Average active minutes by weekday")
        grouped = daily.groupby("DayName", observed=False)["TotalActiveMinutes"].mean().reindex(WEEKDAYS).dropna().reset_index()
        fig = px.bar(
            grouped, x="DayName", y="TotalActiveMinutes", color_discrete_sequence=[COLORS["teal"]],
            labels={"TotalActiveMinutes": "Average active minutes"}, title="Weekly active-time pattern",
        )
        show_chart(fig)

    c3, c4 = st.columns(2)
    with c3:
        chart_title(8, "Daily steps distribution")
        fig = px.histogram(
            daily, x="TotalSteps", nbins=30, color_discrete_sequence=[COLORS["orange"]],
            labels={"TotalSteps": "Daily steps"}, title="Distribution of daily steps",
        )
        show_chart(fig)
    with c4:
        chart_title(9, "Daily calories distribution")
        fig = px.histogram(
            daily, x="Calories", nbins=30, color_discrete_sequence=[COLORS["gold"]],
            title="Distribution of daily calories",
        )
        show_chart(fig)

    c5, c6 = st.columns(2)
    with c5:
        chart_title(10, "Active minutes versus sedentary minutes")
        fig = px.scatter(
            daily, x="SedentaryMinutes", y="TotalActiveMinutes", color="ActivityLevel",
            category_orders={"ActivityLevel": ACTIVITY_ORDER},
            color_discrete_sequence=[COLORS["slate"], COLORS["blue"], COLORS["teal"], COLORS["orange"]],
            opacity=0.65, labels={"TotalActiveMinutes": "Active minutes", "SedentaryMinutes": "Sedentary minutes"},
            title="Daily active and sedentary time", hover_data=["IdLabel", "ActivityDate"],
        )
        show_chart(fig)
    with c6:
        chart_title(11, "Distance versus calories")
        fig = px.scatter(
            daily, x="TotalDistance", y="Calories", trendline="ols", opacity=0.55,
            color_discrete_sequence=[COLORS["blue"]],
            labels={"TotalDistance": "Total distance", "Calories": "Calories"},
            title="Distance and daily energy use", hover_data=["IdLabel", "ActivityDate"],
        )
        show_chart(fig)


elif page == "Sleep & Recovery":
    page_heading(
        "Sleep & Recovery",
        "Sleep duration, efficiency, time in bed, and its observed relationship with activity.",
    )
    if sleep.empty:
        st.info("No sleep records match the selected filters.")
        st.stop()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Sleep records", f"{len(sleep):,}")
    k2.metric("Average sleep", f"{sleep['SleepHours'].mean():.2f} h")
    k3.metric("Average efficiency", f"{sleep['SleepEfficiencyPercent'].mean():.1f}%")
    k4.metric("Below 7 hours", f"{(sleep['TotalMinutesAsleep'] < 420).mean():.1%}")

    c1, c2 = st.columns(2)
    with c1:
        chart_title(12, "Average sleep hours by weekday")
        grouped = sleep.groupby("DayName", observed=False)["SleepHours"].mean().reindex(WEEKDAYS).dropna().reset_index()
        fig = px.bar(
            grouped, x="DayName", y="SleepHours", color_discrete_sequence=[COLORS["teal"]],
            labels={"SleepHours": "Average sleep hours"}, title="Weekly sleep-duration pattern",
        )
        show_chart(fig)
    with c2:
        chart_title(13, "Sleep-duration group distribution")
        groups = (
            sleep["SleepDurationGroup"].value_counts().reindex(SLEEP_ORDER, fill_value=0).rename_axis("SleepDurationGroup").reset_index(name="Records")
        )
        fig = px.bar(
            groups, x="SleepDurationGroup", y="Records",
            category_orders={"SleepDurationGroup": SLEEP_ORDER},
            color_discrete_sequence=[COLORS["blue"]],
            labels={"SleepDurationGroup": "Sleep group"}, title="Sleep records by duration",
        )
        show_chart(fig)

    c3, c4 = st.columns(2)
    with c3:
        chart_title(14, "Daily steps versus sleep duration")
        corr = sleep["TotalSteps"].corr(sleep["SleepHours"])
        fig = px.scatter(
            sleep, x="TotalSteps", y="SleepHours", trendline="ols", opacity=0.55,
            color_discrete_sequence=[COLORS["orange"]],
            labels={"TotalSteps": "Daily steps", "SleepHours": "Sleep hours"},
            title=f"Steps and sleep (correlation {corr:.2f})", hover_data=["IdLabel", "ActivityDate"],
        )
        show_chart(fig)
    with c4:
        chart_title(15, "Sleep-efficiency distribution")
        fig = px.histogram(
            sleep, x="SleepEfficiencyPercent", nbins=25,
            color_discrete_sequence=[COLORS["teal"]],
            labels={"SleepEfficiencyPercent": "Sleep efficiency (%)"},
            title="Distribution of sleep efficiency",
        )
        fig.add_vline(x=sleep["SleepEfficiencyPercent"].mean(), line_dash="dash", line_color=COLORS["orange"])
        show_chart(fig)

    chart_title(16, "Time in bed versus minutes asleep")
    fig = px.scatter(
        sleep, x="TotalTimeInBed", y="TotalMinutesAsleep", trendline="ols", opacity=0.55,
        color_discrete_sequence=[COLORS["blue"]],
        labels={"TotalTimeInBed": "Minutes in bed", "TotalMinutesAsleep": "Minutes asleep"},
        title="Time in bed and sleep duration", hover_data=["IdLabel", "ActivityDate"],
    )
    show_chart(fig)


elif page == "Hourly & Heart Rate":
    page_heading(
        "Hourly & Heart Rate",
        "Intraday movement, calorie use, intensity, and available daily heart-rate summaries.",
    )
    if hourly.empty:
        st.info("No hourly records match the selected filters.")
        st.stop()

    peak_steps = hourly.groupby("HourNumber")["StepTotal"].mean()
    heart = daily.dropna(subset=["AverageHeartRate"]).copy()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Hourly records", f"{len(hourly):,}")
    k2.metric("Peak movement hour", f"{int(peak_steps.idxmax()):02d}:00")
    k3.metric("Heart-rate days", f"{len(heart):,}")
    k4.metric("Average heart rate", "n.a." if heart.empty else f"{heart['AverageHeartRate'].mean():.1f} bpm")

    c1, c2 = st.columns(2)
    with c1:
        chart_title(17, "Average steps by hour")
        grouped = hourly.groupby("HourNumber", as_index=False)["StepTotal"].mean()
        fig = px.line(
            grouped, x="HourNumber", y="StepTotal", markers=True,
            color_discrete_sequence=[COLORS["orange"]],
            labels={"HourNumber": "Hour of day", "StepTotal": "Average steps"},
            title="Hourly movement pattern",
        )
        fig.update_xaxes(dtick=2)
        show_chart(fig)
    with c2:
        chart_title(18, "Average calories by hour")
        grouped = hourly.groupby("HourNumber", as_index=False)["Calories"].mean()
        fig = px.line(
            grouped, x="HourNumber", y="Calories", markers=True,
            color_discrete_sequence=[COLORS["gold"]],
            labels={"HourNumber": "Hour of day", "Calories": "Average calories"},
            title="Hourly calorie pattern",
        )
        fig.update_xaxes(dtick=2)
        show_chart(fig)

    c3, c4 = st.columns(2)
    with c3:
        chart_title(19, "Average intensity by hour")
        grouped = hourly.groupby("HourNumber", as_index=False)["TotalIntensity"].mean()
        fig = px.line(
            grouped, x="HourNumber", y="TotalIntensity", markers=True,
            color_discrete_sequence=[COLORS["teal"]],
            labels={"HourNumber": "Hour of day", "TotalIntensity": "Average total intensity"},
            title="Hourly intensity pattern",
        )
        fig.update_xaxes(dtick=2)
        show_chart(fig)
    with c4:
        chart_title(20, "Average heart rate by participant")
        if heart.empty:
            st.info("No heart-rate records match the selected filters.")
        else:
            grouped = (
                heart.groupby("IdLabel", as_index=False)["AverageHeartRate"].mean().sort_values("AverageHeartRate", ascending=True)
            )
            fig = px.bar(
                grouped, x="AverageHeartRate", y="IdLabel", orientation="h",
                color_discrete_sequence=[COLORS["teal"]],
                labels={"IdLabel": "Participant", "AverageHeartRate": "Average heart rate (bpm)"},
                title="Daily average heart rate by participant",
            )
            show_chart(fig)


else:
    page_heading(
        "Insights & Data Quality",
        "Case-study findings, practical recommendations, data limitations, and filtered downloads.",
    )

    valid_full = daily_all.loc[daily_all["PossibleNonWearDay"] == 0].copy()
    full_sleep = valid_full.dropna(subset=["SleepHours"])
    weekday_avg = valid_full.groupby("DayName", observed=False)["TotalSteps"].mean()
    peak_day = weekday_avg.idxmax()
    peak_hour = int(hourly_all.groupby("HourNumber")["StepTotal"].mean().idxmax())
    steps_cal_corr = valid_full["TotalSteps"].corr(valid_full["Calories"])
    steps_sleep_corr = full_sleep["TotalSteps"].corr(full_sleep["SleepHours"])

    st.markdown("### Key findings")
    findings = [
        f"The dataset covers {daily_all['Id'].nunique()} participants and {len(daily_all):,} daily activity records.",
        f"After excluding {int(daily_all['PossibleNonWearDay'].sum())} possible non-wear days, average daily steps are {valid_full['TotalSteps'].mean():,.0f}.",
        f"The 10,000-step target is achieved on {valid_full['Met10000StepGoal'].mean():.1%} of valid activity days.",
        f"Average sedentary time is {valid_full['SedentaryMinutes'].mean():.0f} minutes per day.",
        f"Average sleep is {full_sleep['SleepHours'].mean():.2f} hours, and {(full_sleep['SleepHours'] < 7).mean():.1%} of sleep records are below seven hours.",
        f"{peak_day} has the highest average steps, while movement peaks around {peak_hour:02d}:00.",
        f"Steps and calories have a moderate positive correlation ({steps_cal_corr:.2f}). Steps and sleep show a weak relationship ({steps_sleep_corr:.2f}).",
    ]
    for item in findings:
        st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)

    st.markdown("### Recommendations")
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown(
            '<div class="insight-card"><b>Reduce long sedentary periods</b><br>Use movement reminders and short activity prompts during inactive hours.</div>',
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            '<div class="insight-card"><b>Use achievable step milestones</b><br>Personalize gradual targets instead of relying only on a universal 10,000-step goal.</div>',
            unsafe_allow_html=True,
        )
    with r3:
        st.markdown(
            '<div class="insight-card"><b>Support sleep consistency</b><br>Pair activity messaging with bedtime routines and recovery-focused content.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Data-quality summary")
    quality = pd.DataFrame(
        {
            "Measure": [
                "Daily activity records", "Participants", "Possible non-wear days",
                "Participant-date sleep records", "Participant-date weight records",
                "Participant-date heart-rate records", "Hourly activity records",
            ],
            "Value": [
                len(daily_all), daily_all["Id"].nunique(), int(daily_all["PossibleNonWearDay"].sum()),
                int(daily_all["TotalMinutesAsleep"].notna().sum()),
                int(daily_all["WeightKg"].notna().sum()),
                int(daily_all["AverageHeartRate"].notna().sum()), len(hourly_all),
            ],
        }
    )
    st.dataframe(quality, hide_index=True, use_container_width=True)

    st.markdown("### Limitations")
    st.markdown(
        """
        <div class="note-card">
        This public Fitbit sample covers a short observation period and a small, self-selected group. Data availability differs by measure, particularly for sleep, weight, and heart rate. Possible non-wear days are rule-based flags. The dashboard describes associations and should not be used for medical diagnosis or causal conclusions.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Download filtered data")
    d1, d2 = st.columns(2)
    d1.download_button(
        "Download filtered daily data",
        dataframe_csv(daily),
        file_name="filtered_daily_fitness.csv",
        mime="text/csv",
        use_container_width=True,
    )
    d2.download_button(
        "Download filtered hourly data",
        dataframe_csv(hourly),
        file_name="filtered_hourly_activity.csv",
        mime="text/csv",
        use_container_width=True,
    )

    with st.expander("Preview filtered daily records"):
        preview_cols = [
            "IdLabel", "ActivityDate", "TotalSteps", "Calories", "TotalActiveMinutes",
            "SedentaryMinutes", "SleepHours", "SleepEfficiencyPercent", "AverageHeartRate",
        ]
        st.dataframe(daily[preview_cols], hide_index=True, use_container_width=True)

