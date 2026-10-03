# Fitness Activity and Recovery Analytics

**Python • Pandas • Plotly • Streamlit | Fitbit/Bellabeat case study**

An interactive dashboard exploring daily activity, sleep, hourly movement and data completeness.

## Business question

What activity and recovery patterns appear in the sample, and what engagement ideas could a wellness product test?

## Data

The prepared daily dataset contains **940 participant-day records across 33 participants**. An hourly dataset supports movement and energy-use comparisons.

The data contains repeated observations per participant; participant-days are not independent people.

## Application pages

1. Executive Overview.
2. Activity Analysis.
3. Sleep & Recovery.
4. Hourly & Heart Rate.
5. Insights & Data Quality.

The app contains 20 numbered chart views, participant/date filters, optional exclusion of possible non-wear days and CSV downloads.

[Open the published app](https://fitness-analytics-app-wnhyjkst8nzfp9wwa5pwxv.streamlit.app/)

## Findings

Using the prepared daily data after excluding records flagged as possible non-wear days:

| Measure | Result |
|---|---:|
| Average daily steps | Approximately 8,319 |
| Average sleep in available sleep records | Approximately 7.04 hours |
| Available sleep records below seven hours | 43.90% |

The sleep percentage uses available sleep records, not every activity record. App values change with filters.

## Recommendations

Test gradual step milestones, movement reminders and sleep-consistency messaging. Measure uptake and behaviour changes before claiming product impact.

## Run locally

~~~bash
git clone https://github.com/manish-kr0722/fitness-analytics-streamlit.git
cd fitness-analytics-streamlit
python -m venv .venv
~~~

Activate the environment:

~~~bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
~~~

~~~bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
~~~

The app uses files in the data folder relative to app.py. The original second-level heart-rate export is not required to run the app.

## Limitations

This is a small, self-selected sample covering a short period. Sleep, weight and heart-rate coverage differ. Possible non-wear days are rule-based flags rather than confirmed device non-use.

Associations do not establish causal effects. The dashboard is not a medical diagnostic tool. This repository contains prepared datasets and the app; it does not include the complete raw-to-prepared SQL pipeline.

## Repository files

- [app.py](app.py)
- [data/daily_fitness_master.csv](data/daily_fitness_master.csv)
- [data/hourly_activity_master.csv](data/hourly_activity_master.csv)
- [requirements.txt](requirements.txt)
- [run_app.bat](run_app.bat)
- [run_app.sh](run_app.sh)

## Author

**Manish Kumar** — banking professional transitioning into Data Analytics.

[LinkedIn](https://www.linkedin.com/in/manish071096/) · [GitHub](https://github.com/manish-kr0722)
