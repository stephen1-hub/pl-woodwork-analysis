from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Premier League Shot Post Analysis",
    page_icon="⚽",
    layout="wide"
)

DATA_DIR = Path("data/processed")


# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():
    required_files = {
        "matches": "match_summary.csv",
        "team_shooting": "team_shooting_summary.csv",
        "players": "player_woodwork_summary.csv",
        "teams": "team_woodwork_summary.csv",
    }

    loaded = {}

    for key, filename in required_files.items():
        file_path = DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing dataset: {file_path}. "
                "Run export_analysis.py from the project folder first."
            )

        loaded[key] = pd.read_csv(file_path)

    return loaded


try:
    data = load_data()
except Exception as error:
    st.error(f"Unable to load dashboard datasets: {error}")
    st.stop()


matches = data["matches"].copy()
team_shooting = data["team_shooting"].copy()
players = data["players"].copy()
teams = data["teams"].copy()


# ==================================================
# DATA PREPARATION
# ==================================================

required_match_columns = [
    "match_id", "matchweek", "home_team", "away_team",
    "score", "total_shots", "woodwork_events", "goals",
    "total_xg", "shots_on_target"
]

missing_match_columns = [
    column for column in required_match_columns
    if column not in matches.columns
]

if missing_match_columns:
    st.error(
        "The match summary is missing required columns: "
        + ", ".join(missing_match_columns)
    )
    st.stop()

matches["matchweek"] = pd.to_numeric(
    matches["matchweek"], errors="coerce"
)

numeric_columns = [
    "total_shots",
    "woodwork_events",
    "woodwork_per_100_shots",
    "shots_on_target",
    "blocked_shots",
    "goals",
    "total_xg",
    "matches_with_woodwork",
]

for frame in [matches, team_shooting, players, teams]:
    for column in numeric_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(
                frame[column], errors="coerce"
            )

if "match_date" in matches.columns:
    matches["match_date"] = pd.to_datetime(
        matches["match_date"], errors="coerce"
    )
    matches = matches.sort_values(
        ["matchweek", "match_date"],
        na_position="last"
    )
else:
    matches = matches.sort_values("matchweek")


# ==================================================
# SIDEBAR AND MATCHWEEK FILTER
# ==================================================

st.sidebar.title("⚽ Shot Analysis")
st.sidebar.markdown("Premier League 2026/27")
st.sidebar.markdown("---")

matchweeks = sorted(
    matches["matchweek"].dropna().unique().tolist()
)

selected_weeks = st.sidebar.multiselect(
    "Select Matchweeks",
    options=matchweeks,
    default=matchweeks,
    format_func=lambda week: f"Matchweek {int(week)}"
)

# An empty selection is treated as All Matchweeks.
if len(selected_weeks) == 0:
    selected_matches = matches.copy()
else:
    selected_matches = matches[
        matches["matchweek"].isin(selected_weeks)
    ].copy()

selected_match_ids = selected_matches["match_id"].tolist()

if "match_id" in team_shooting.columns:
    filtered_team_shooting = team_shooting[
        team_shooting["match_id"].isin(selected_match_ids)
    ].copy()
else:
    filtered_team_shooting = team_shooting.iloc[0:0].copy()

all_matchweeks_selected = (
    len(selected_weeks) == 0
    or set(selected_weeks) == set(matchweeks)
)


# ==================================================
# HEADER
# ==================================================

st.title("⚽ Premier League Shot Post Analysis")

st.markdown(
    """
    **2026/27 Season | Matchweeks 1–10**

    An analytical dashboard examining shooting performance,
    player and team woodwork events, and shot outcomes.
    """
)

st.markdown("---")


# ==================================================
# OVERALL KPI SECTION
# ==================================================

total_shots = int(
    selected_matches["total_shots"].fillna(0).sum()
)
total_woodwork = int(
    selected_matches["woodwork_events"].fillna(0).sum()
)
total_goals = int(
    selected_matches["goals"].fillna(0).sum()
)
total_xg = selected_matches["total_xg"].sum()

woodwork_rate = (
    total_woodwork / total_shots * 100
    if total_shots > 0 else 0
)

matches_covered = len(selected_matches)

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Shots", f"{total_shots:,}")
col2.metric("Woodwork Events", f"{total_woodwork:,}")
col3.metric("Goals", f"{total_goals:,}")
col4.metric("Woodwork / 100 Shots", f"{woodwork_rate:.2f}")
col5.metric("Matches Covered", f"{matches_covered:,}")

st.markdown("---")


# ==================================================
# DASHBOARD TABS
# ==================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Team Analysis",
    "Player Analysis",
    "Match Analysis",
    "Data Quality",
])


# ==================================================
# TAB 1: OVERVIEW
# ==================================================

with tab1:
    st.subheader("Shooting Performance by Matchweek")

    # Define weekly before using it in any chart or table.
    weekly = (
        selected_matches
        .groupby("matchweek", as_index=False)
        .agg(
            total_shots=("total_shots", "sum"),
            woodwork_events=("woodwork_events", "sum"),
            goals=("goals", "sum"),
        )
    )

    if not weekly.empty:
        trend_chart = px.line(
            weekly,
            x="matchweek",
            y=["total_shots", "woodwork_events", "goals"],
            markers=True,
            title="Shooting and Woodwork Trends",
            labels={
                "matchweek": "Matchweek",
                "value": "Number of events",
                "variable": "Metric",
            },
        )
        st.plotly_chart(trend_chart, use_container_width=True)
    else:
        st.info("No match data is available for this selection.")

    st.markdown("---")

    left, right = st.columns(2)

    with left:
        st.subheader("Woodwork Events by Matchweek")

        if not weekly.empty:
            woodwork_chart = px.bar(
                weekly,
                x="matchweek",
                y="woodwork_events",
                text="woodwork_events",
                title="Woodwork Events",
                labels={
                    "matchweek": "Matchweek",
                    "woodwork_events": "Woodwork Events",
                },
            )
            st.plotly_chart(
                woodwork_chart,
                use_container_width=True
            )

    with right:
        st.subheader("Matchweek Shooting Summary")
        st.dataframe(
            weekly,
            use_container_width=True,
            hide_index=True
        )


# ==================================================
# TAB 2: TEAM ANALYSIS
# ==================================================

with tab2:
    st.subheader("Team Woodwork Analysis")

    if all_matchweeks_selected:
        team_view = teams.copy()
    elif not filtered_team_shooting.empty:
        team_view = (
            filtered_team_shooting
            .groupby("team_name", as_index=False)
            .agg(
                total_shots=("total_shots", "sum"),
                woodwork_events=("woodwork_events", "sum"),
            )
        )

        team_view["woodwork_per_100_shots"] = (
            100 * team_view["woodwork_events"]
            / team_view["total_shots"].replace(0, pd.NA)
        )
    else:
        team_view = pd.DataFrame(
            columns=[
                "team_name",
                "total_shots",
                "woodwork_events",
                "woodwork_per_100_shots",
            ]
        )

    if not team_view.empty:
        team_view = team_view.sort_values(
            "woodwork_events",
            ascending=False
        )

        left, right = st.columns(2)

        with left:
            team_count_chart = px.bar(
                team_view.sort_values(
                    "woodwork_events",
                    ascending=True
                ),
                x="woodwork_events",
                y="team_name",
                orientation="h",
                title="Woodwork Events by Team",
                labels={
                    "team_name": "Team",
                    "woodwork_events": "Woodwork Events",
                },
            )
            st.plotly_chart(
                team_count_chart,
                use_container_width=True
            )

        with right:
            team_rate_chart = px.bar(
                team_view.sort_values(
                    "woodwork_per_100_shots",
                    ascending=True
                ),
                x="woodwork_per_100_shots",
                y="team_name",
                orientation="h",
                title="Woodwork Rate per 100 Shots",
                labels={
                    "team_name": "Team",
                    "woodwork_per_100_shots": "Rate per 100 shots",
                },
            )
            st.plotly_chart(
                team_rate_chart,
                use_container_width=True
            )

        st.markdown("### Team Statistics")
        st.dataframe(
            team_view,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No team data is available for this selection.")

    st.caption(
        "Team rates are descriptive. Teams with fewer shots "
        "may have more volatile rates."
    )


# ==================================================
# TAB 3: PLAYER ANALYSIS
# ==================================================

with tab3:
    st.subheader("Player Woodwork Analysis")

    min_shots = st.slider(
        "Minimum shots taken",
        min_value=1,
        max_value=50,
        value=5,
    )

    player_view = players.copy()

    if "total_shots" in player_view.columns:
        player_view = player_view[
            player_view["total_shots"] >= min_shots
        ].copy()

    sort_columns = [
        column for column in [
            "woodwork_events",
            "woodwork_per_100_shots",
        ]
        if column in player_view.columns
    ]

    if sort_columns:
        player_view = player_view.sort_values(
            sort_columns,
            ascending=[False] * len(sort_columns)
        )

    left, right = st.columns(2)

    with left:
        st.markdown("### Most Woodwork Events")

        if not player_view.empty:
            top_players = player_view.head(15).sort_values(
                "woodwork_events",
                ascending=True
            )

            player_count_chart = px.bar(
                top_players,
                x="woodwork_events",
                y="player_name",
                orientation="h",
                title="Top Players by Woodwork Events",
                labels={
                    "player_name": "Player",
                    "woodwork_events": "Woodwork Events",
                },
            )
            st.plotly_chart(
                player_count_chart,
                use_container_width=True
            )
        else:
            st.info("No players meet the selected minimum-shot threshold.")

    with right:
        st.markdown("### Highest Woodwork Rates")

        if (
            not player_view.empty
            and "woodwork_events" in player_view.columns
            and "woodwork_per_100_shots" in player_view.columns
        ):
            rate_players = (
                player_view[
                    player_view["woodwork_events"] > 0
                ]
                .sort_values(
                    "woodwork_per_100_shots",
                    ascending=False
                )
                .head(15)
                .sort_values(
                    "woodwork_per_100_shots",
                    ascending=True
                )
            )

            if not rate_players.empty:
                player_rate_chart = px.bar(
                    rate_players,
                    x="woodwork_per_100_shots",
                    y="player_name",
                    orientation="h",
                    title="Woodwork per 100 Shots",
                    labels={
                        "player_name": "Player",
                        "woodwork_per_100_shots": "Rate",
                    },
                )
                st.plotly_chart(
                    player_rate_chart,
                    use_container_width=True
                )
            else:
                st.info("No woodwork events found for these players.")
        else:
            st.info("Player rate data is unavailable.")

    st.markdown("### Player Statistics")
    st.dataframe(
        player_view,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Player statistics cover all currently collected matches, "
        "not just the selected matchweeks. Interpret rates with "
        "caution, especially for players with few shots."
    )


# ==================================================
# TAB 4: MATCH ANALYSIS
# ==================================================

with tab4:
    st.subheader("Match-Level Shooting Analysis")

    if not selected_matches.empty:
        selected_match = st.selectbox(
            "Select a match",
            options=selected_matches["match_id"].tolist(),
            format_func=lambda match_id: (
                lambda row: (
                    f"MW {int(row['matchweek'])} | "
                    f"{row['home_team']} vs {row['away_team']} "
                    f"({row['score']})"
                )
            )(
                selected_matches[
                    selected_matches["match_id"] == match_id
                ].iloc[0]
            ),
        )

        match_row = selected_matches[
            selected_matches["match_id"] == selected_match
        ].iloc[0]

        st.markdown(
            f"### {match_row['home_team']} vs "
            f"{match_row['away_team']}"
        )
        st.write(f"Score: {match_row['score']}")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Shots",
            int(match_row["total_shots"])
        )
        col2.metric(
            "Shots on Target",
            int(match_row["shots_on_target"])
        )
        col3.metric(
            "Woodwork",
            int(match_row["woodwork_events"])
        )

        match_xg = match_row["total_xg"]
        col4.metric(
            "Total xG",
            f"{match_xg:.2f}" if pd.notna(match_xg) else "N/A"
        )

        st.markdown("---")
        st.markdown("### Team Comparison")

        if not filtered_team_shooting.empty:
            match_teams = filtered_team_shooting[
                filtered_team_shooting["match_id"] == selected_match
            ]

            if not match_teams.empty:
                st.dataframe(
                    match_teams,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info(
                    "No team-level shooting records are available "
                    "for this match."
                )
        else:
            st.info("No team-level shooting data is available.")
    else:
        st.info("No matches are available for this selection.")


# ==================================================
# TAB 5: DATA QUALITY
# ==================================================

with tab5:
    st.subheader("Data Coverage and Validation")

    st.markdown(
        """
        The analysis currently covers the first 10 matchweeks.
        One Matchweek 5 fixture remains unresolved.
        """
    )

    expected_fixtures = 100
    matches_with_data = len(matches)
    unresolved_fixtures = max(
        expected_fixtures - matches_with_data,
        0
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Expected Fixtures", expected_fixtures)
    col2.metric("Matches with Shot Data", matches_with_data)
    col3.metric("Unresolved Fixtures", unresolved_fixtures)

    st.markdown("---")
    st.markdown("### Matchweek Coverage")

    coverage = (
        matches.groupby("matchweek")
        .agg(
            matches_with_shots=("match_id", "nunique"),
            total_shots=("total_shots", "sum"),
            woodwork_events=("woodwork_events", "sum"),
        )
        .reset_index()
    )

    coverage["expected_matches"] = 10
    coverage["coverage_status"] = coverage[
        "matches_with_shots"
    ].apply(
        lambda count: "Complete" if count == 10 else "Incomplete"
    )

    st.dataframe(
        coverage,
        use_container_width=True,
        hide_index=True
    )

    st.warning(
        "One Matchweek 5 fixture has no verified shot dataset. "
        "It is excluded from the shooting and woodwork totals. "
        "It must not be interpreted as a zero-woodwork match."
    )

    st.markdown("### Dataset Information")

    dataset_info = pd.DataFrame([
        {
            "Dataset": "Match summary",
            "Records": len(matches),
        },
        {
            "Dataset": "Team shooting summary",
            "Records": len(team_shooting),
        },
        {
            "Dataset": "Player woodwork summary",
            "Records": len(players),
        },
        {
            "Dataset": "Team woodwork summary",
            "Records": len(teams),
        },
    ])

    st.dataframe(
        dataset_info,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# FOOTER
# ==================================================

st.markdown("---")

st.caption(
    "Premier League Shot Post Analysis | 2026/27 | "
    "Built with Python, PostgreSQL, Pandas and Streamlit."
)