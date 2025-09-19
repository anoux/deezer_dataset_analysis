import duckdb
import streamlit as st
import pandas as pd

# Connect to DuckDB
con = duckdb.connect("deezer.db")

st.title("🎶 Deezer Music Dashboard")

# KPI
kpi = con.execute("""
    SELECT 
        COUNT(DISTINCT ArtistId) AS artists,
        COUNT(DISTINCT AlbumId) AS albums,
        COUNT(DISTINCT TrackTitle) AS tracks, 
        AVG(TrackDurationSeconds) AS avg_duration_seconds
    FROM deezer_table
    WHERE TrackDuration IS NOT NULL;
""").df().iloc[0]

# commas as separators
artists_fmt = f"{kpi['artists']:,.0f}"
albums_fmt = f"{kpi['albums']:,.0f}"
tracks_fmt = f"{kpi['tracks']:,.0f}"
avg_duration_fmt = f"{kpi['avg_duration_seconds']:,.2f}"

avg_secs = kpi['avg_duration_seconds']

# convert to minutes + seconds
minutes = int(avg_secs // 60)
seconds = int(avg_secs % 60)
avg_duration_fmt = f"{minutes}:{seconds:02d}"

# Streamlit metrics
st.metric("Artists", artists_fmt)
st.metric("Albums", albums_fmt)
st.metric("Tracks", tracks_fmt)
st.metric("Avg Track Duration (s)", avg_duration_fmt)

# Tabs
tab1, tab2, tab3 = st.tabs(["👨‍🎤 Artists", "💿 Albums", "🎵 Tracks"])

with tab1:
    st.subheader("Top 20 Artists by Fans")
    df = con.execute("""
        SELECT ArtistName, MAX(ArtistNbFan) as fans
        FROM deezer_table
        GROUP BY ArtistName
        ORDER BY fans DESC
        LIMIT 20
    """).df()
    st.bar_chart(df.set_index("ArtistName"))

with tab2:
    st.subheader("Albums Released per Year")
    df = con.execute("""
        SELECT SUBSTRING(AlbumReleaseDate,1,4) AS year, COUNT(*) as album_count
        FROM deezer_table
        WHERE AlbumReleaseDate IS NOT NULL
          AND SUBSTRING(AlbumReleaseDate,1,4) ~ '^[0-9]{4}$'  -- ensure it's a 4-digit year
          AND CAST(SUBSTRING(AlbumReleaseDate,1,4) AS INT) BETWEEN 1800 AND 2030
        GROUP BY year
        ORDER BY year
    """).df()
    st.line_chart(df.set_index("year"))

with tab3:
    st.subheader("Track BPM vs Gain")
    df = con.execute("""
        SELECT TrackBPM, TrackGain, TrackTitle
        FROM deezer_table
        WHERE TrackBPM IS NOT NULL AND TrackGain IS NOT NULL
        LIMIT 500
    """).df()
    st.scatter_chart(df, x="TrackBPM", y="TrackGain")
