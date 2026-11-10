# Premier League Shot & Woodwork Analysis (2026/27)

## Project Overview

The **Premier League Shot & Woodwork Analysis** is a football data engineering and analytics project that investigates shooting performance and woodwork events across the first 10 matchweeks of the 2026/27 Premier League season.

The project uses football match and shot-event data from FotMob to build an end-to-end data pipeline involving Python, PostgreSQL, SQL and Streamlit.

The primary objective is to understand how frequently teams and players hit the woodwork, how these events are distributed across matchweeks, and how shooting performance differs between teams.

Rather than focusing exclusively on goals, the analysis examines a broader range of shooting indicators to provide additional insight into attacking performance.

## Project Objectives

- Extract match fixtures and shot-event data.
- Build a Python ETL pipeline for data extraction, transformation and loading.
- Store structured football data in PostgreSQL.
- Analyse shooting performance using SQL.
- Identify teams and players with the highest woodwork counts.
- Calculate woodwork frequency per 100 shots.
- Develop an interactive Streamlit dashboard.
- Validate analytical outputs against database records.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data extraction and transformation |
| Pandas | Data cleaning and manipulation |
| PostgreSQL | Relational database |
| SQL | Data analysis and aggregation |
| SQLAlchemy | Database connectivity |
| Streamlit | Interactive dashboard |
| Plotly | Data visualisation |
| Docker | PostgreSQL environment |
| Git & GitHub | Version control and project publishing |
| uv | Python dependency management |

## Data Source

**Source:** FotMob

The project uses:
- Premier League fixture information.
- Match identifiers and match URLs.
- Individual match shot-event records.
- Player and team information.
- Shooting indicators such as event type, shot type, expected goals and shot outcome.

The initial analysis covers matchweeks 1–10 of the 2026/27 season.

## Data Engineering Architecture

The project follows an ETL (Extract, Transform, Load) workflow.

```text
              FOTMOB DATA
                   |
                   v
          PYTHON EXTRACTION
                   |
                   v
             RAW CSV DATA
                   |
                   v
          DATA TRANSFORMATION
          - Data validation
          - Event classification
          - Duplicate checks
          - Missing-file checks
                   |
                   v
              POSTGRESQL
                   |
                   v
              SQL ANALYSIS
          - Team performance
          - Player performance
          - Matchweek summaries
          - Woodwork analysis
                   |
                   v
           PROCESSED CSV DATA
                   |
                   v
          STREAMLIT DASHBOARD
                   |
                   v
           FOOTBALL INSIGHTS
```

## Key Analytical Metrics

The analysis includes:

| Metric | Description |
|---|---|
| Total Shots | Number of recorded shot events |
| Shots on Target | Attempts classified as on target |
| Blocked Shots | Attempts blocked by defenders |
| Goals | Recorded goal events |
| Expected Goals (xG) | Expected goal value of recorded attempts |
| Woodwork Events | Attempts explicitly classified as `Post` |
| Woodwork per 100 Shots | Woodwork events divided by total shots, multiplied by 100 |

**Woodwork classification methodology**

An event is classified as a woodwork event when FotMob's `eventType` is explicitly recorded as `Post`.

This avoids incorrectly classifying every missed or on-target attempt as a woodwork event.

## Dataset Coverage

The initial dataset covers 100 Premier League fixtures across 10 matchweeks.

| Data Quality Indicator | Result |
|---|---:|
| Total fixtures | 100 |
| Unique fixtures | 100 |
| Fixtures with shot data | 99 |
| Fixtures pending shot-data resolution | 1 |
| Total recorded shots | 2,703 |
| Total woodwork events | 41 |
| Total goals | 272 |

The overall woodwork frequency is:

**1.52 woodwork events per 100 recorded shots.**

## Key Findings

### 1. Team Woodwork Analysis

Manchester United recorded the highest number of woodwork events, with six.

Crystal Palace recorded the highest woodwork frequency relative to its shooting volume.

| Team | Shots | Woodwork | Per 100 Shots |
|---|---:|---:|---:|
| Manchester United | 194 | 6 | 3.09 |
| Crystal Palace | 104 | 5 | 4.81 |
| Brighton & Hove Albion | 170 | 5 | 2.94 |
| Manchester City | 151 | 4 | 2.65 |
| Fulham | 129 | 3 | 2.33 |

### 2. Player Woodwork Analysis

The leading player by woodwork count was Iliman Ndiaye, with three events.

| Player | Shots | Woodwork | Per 100 Shots |
|---|---:|---:|---:|
| Iliman Ndiaye | 17 | 3 | 17.65 |
| Jean-Philippe Mateta | 6 | 2 | 33.33 |
| Yéremi Pino | 14 | 2 | 14.29 |
| Gonzalo García | 20 | 2 | 10.00 |
| Bruno Fernandes | 31 | 2 | 6.45 |

Player rates should be interpreted cautiously because some players have relatively small shooting samples.

### 3. Matchweek Analysis

Woodwork events were distributed across all ten matchweeks.

| Matchweek | Matches with Data | Shots | Woodwork |
|---|---:|---:|---:|
| 1 | 10 | 275 | 4 |
| 2 | 10 | 275 | 4 |
| 3 | 10 | 256 | 6 |
| 4 | 10 | 259 | 5 |
| 5 | 9 | 290 | 2 |
| 6 | 10 | 267 | 3 |
| 7 | 10 | 267 | 6 |
| 8 | 10 | 260 | 3 |
| 9 | 10 | 283 | 5 |
| 10 | 10 | 271 | 3 |

## Streamlit Dashboard

The interactive dashboard provides:

- Overall shooting performance KPIs.
- Matchweek filtering.
- Shooting trends across matchweeks.
- Woodwork event trends.
- Team shooting comparisons.
- Player woodwork analysis.
- Match summaries.
- Data coverage and quality information.

Users can explore the data by selecting individual matchweeks or viewing the complete dataset.

**Dashboard screenshots:** To be added before publication.

## Project Structure

```text
pl-woodwork-analysis/
│
├── data/
│   ├── raw/
│   │   ├── fixtures_mw1_mw10.csv
│   │   └── match_*_shots.csv
│   │
│   └── processed/
│       ├── shots_cleaned.csv
│       ├── match_summary.csv
│       ├── team_shooting_summary.csv
│       ├── player_woodwork_summary.csv
│       └── team_woodwork_summary.csv
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── get_fixtures.py
│   ├── validate_fixtures.py
│   ├── load_fixtures.py
│   ├── extract_matchweek.py
│   ├── validate_matchweek.py
│   └── rebuild_matchweek_report.py
│
├── export_analysis.py
├── app.py
├── app59.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd pl-woodwork-analysis
```

### 2. Create a virtual environment

```bash
uv venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
uv sync
```

If using the requirements-based installation instead:

```bash
uv pip install pandas requests sqlalchemy psycopg2-binary python-dotenv matplotlib plotly beautifulsoup4 streamlit
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a guide.

```env
DATABASE_URL=postgresql+psycopg2://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME
```

Do not commit your `.env` file or database credentials to GitHub.

### 5. Start PostgreSQL

Ensure Docker Desktop is running and your PostgreSQL container and database are configured.

### 6. Run the dashboard

```bash
streamlit run app59.py
```

The dashboard will be available through the local Streamlit URL displayed in your terminal.

## Data Quality and Limitations

- The initial analysis covers the first ten matchweeks.
- One fixture in Matchweek 5 remains unresolved and does not have confirmed shot data.
- Results represent collected and validated records, not necessarily every possible event in the competition.
- Woodwork classification depends on FotMob's explicit `Post` event label.
- Player and team rates can be affected by small sample sizes.
- Woodwork frequency should not independently be interpreted as a measure of finishing quality, player ability or luck.

## Future Improvements

Potential extensions include:

- Expanding coverage to additional matchweeks.
- Improving automated data validation and monitoring.
- Adding team and player filters.
- Introducing shot-location visualisations.
- Analysing woodwork events by shot situation and body part.
- Exploring relationships between expected goals and woodwork events.
- Deploying the Streamlit dashboard publicly.

## Conclusion

This project demonstrates how football event data can be transformed into structured analytical information through a practical data engineering workflow.

By combining Python ETL, PostgreSQL, SQL and Streamlit, the project creates a reusable foundation for analysing shooting performance and woodwork events in professional football.

It also demonstrates the importance of data quality, validation and transparent methodology when producing football analytics.

---

**Built using Python, PostgreSQL, SQL and Streamlit.**

*Football Data Engineering | Football Analytics | Data Visualisation*
