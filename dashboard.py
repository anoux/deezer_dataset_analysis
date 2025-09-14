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
        AVG(EXTRACT(EPOCH FROM TrackDuration)) AS avg_duration
    FROM deezer_table
""").df().iloc[0]

st.metric("Artists", kpi["artists"])
st.metric("Albums", kpi["albums"])
st.metric("Tracks", kpi["tracks"])
st.metric("Avg Track Duration (s)", round(kpi["avg_duration"], 2))

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
