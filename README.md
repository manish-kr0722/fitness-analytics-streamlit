# Fitness Analytics Streamlit App

Interactive dashboard for the Bellabeat / Fitbit fitness-data case study. The app uses compact prepared datasets, global filters, KPI cards, 20 Plotly charts, key findings, data-quality notes, and CSV downloads.

## Run locally

On Windows, you can double-click `run_app.bat` to install the required packages and start the dashboard.

For a terminal-based setup:

1. Open a terminal in this folder.
2. Install the packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

## Dashboard pages

- Executive Overview
- Activity Analysis
- Sleep & Recovery
- Hourly & Heart Rate
- Insights & Data Quality

## Included data

- `data/daily_fitness_master.csv`: one record per participant and activity date, with sleep, weight, and daily heart-rate summaries where available.
- `data/hourly_activity_master.csv`: joined hourly steps, calories, and intensity.

The original second-level heart-rate file is not required when running the app. Participant IDs are anonymous. The analysis is descriptive and does not support medical diagnosis or causal claims.

## Deploy on Streamlit Community Cloud

Upload this folder to a GitHub repository, create a new Streamlit app, and select `app.py` as the entry point. The included `requirements.txt` and `.streamlit/config.toml` provide the required environment and theme.
