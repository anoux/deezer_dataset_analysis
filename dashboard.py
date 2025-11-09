import duckdb
import streamlit as st
import altair as alt
import pandas as pd

# Connect to DuckDB
con = duckdb.connect("deezer.db")

st.title("Deezer Music Dashboard 🎶")

st.markdown("### Some high-level KPIs")

col1, col2, col3 = st.columns(3)

# KPIs
kpi_counts = con.execute("""
    SELECT 
        COUNT(DISTINCT AlbumGenreName) AS genres,
        COUNT(DISTINCT ArtistId) AS artists,
        COUNT(DISTINCT AlbumId) AS albums,
        COUNT(DISTINCT TrackTitle) AS tracks,
        AVG(TrackDurationSeconds) AS avg_duration_seconds,      
    FROM deezer_table
    WHERE TrackDuration IS NOT NULL;
""").df().iloc[0]

# KPIs part 2 - averages
kpi_avg_1 = con.execute("""
    SELECT 
    AVG(artist_count) AS avg_artist_per_genre
FROM (
    SELECT 
        AlbumGenreName,
        COUNT(DISTINCT ArtistId) AS artist_count
    FROM deezer_table
    GROUP BY AlbumGenreName
) AS artist_genre_summary;
""").df().iloc[0]

kpi_avg_2 = con.execute("""
    SELECT 
    AVG(album_count) AS avg_album_per_artist
FROM (
    SELECT 
        ArtistId,
        COUNT(DISTINCT AlbumGenreName) AS album_count
    FROM deezer_table
    GROUP BY ArtistId
) AS album_artist_summary;
""").df().iloc[0]

kpi_avg_3 = con.execute("""
    SELECT 
    AVG(track_count) AS avg_track_per_album
FROM (
    SELECT 
        AlbumId,
        COUNT(DISTINCT TrackTitle) AS track_count
    FROM deezer_table
    GROUP BY AlbumID
) AS track_album_summary;
""").df().iloc[0]

# --- Format helpers ---
def fmt_int(value):
    """Format integer KPIs with comma separators (e.g., 1,234)."""
    return f"{value:,.0f}"

def fmt_float(value, decimals=2):
    """Format float KPIs with comma separators and decimals (e.g., 1,234.56)."""
    return f"{value:,.{decimals}f}"

# --- Basic counts ---
genres_fmt  = fmt_int(kpi_counts['genres'])
artists_fmt = fmt_int(kpi_counts['artists'])
albums_fmt  = fmt_int(kpi_counts['albums'])
tracks_fmt  = fmt_int(kpi_counts['tracks'])

# --- Ratios and averages ---
artist_per_genre = kpi_counts['artists'] / kpi_counts['genres']
album_per_artist = kpi_counts['albums'] / kpi_counts['artists']
track_per_album  = kpi_counts['tracks'] / kpi_counts['albums']

genre_per_album_fmt       = fmt_float(artist_per_genre)
album_per_artist_fmt      = fmt_float(album_per_artist)
track_per_album_fmt       = fmt_float(track_per_album)
avg_artist_per_genre_fmt  = fmt_float(kpi_avg_1['avg_artist_per_genre'])
avg_album_per_artist_fmt  = fmt_float(kpi_avg_2['avg_album_per_artist'])
avg_track_per_album_fmt   = fmt_float(kpi_avg_3['avg_track_per_album'])

# --- Average track duration (convert seconds to mm:ss) ---
avg_secs = kpi_counts['avg_duration_seconds']
minutes, seconds = divmod(int(avg_secs), 60)
avg_duration_fmt = f"{minutes}:{seconds:02d}"


# convert to minutes + seconds
avg_secs = kpi_counts['avg_duration_seconds']
minutes = int(avg_secs // 60)
seconds = int(avg_secs % 60)
avg_duration_fmt = f"{minutes}:{seconds:02d}"

# Streamlit metrics

with col1:
    
    st.metric("No. Genres", genres_fmt)
    st.metric("No. Artists", artists_fmt)
    st.metric("No. Albums", albums_fmt)
    st.metric("No. Tracks", tracks_fmt)

with col2:
    
    st.metric("No. Artists/Genre", genre_per_album_fmt)
    st.metric("No. Albums/Artist", album_per_artist_fmt)
    st.metric("No. Tracks/Album", track_per_album_fmt)
    
    
with col3:
    st.metric("Avg Artists per Genre", avg_artist_per_genre_fmt)
    st.metric("Avg Albums per Artist", avg_album_per_artist_fmt)
    st.metric("Avg Tracks per Album", avg_track_per_album_fmt)
    st.metric("Avg Track Duration", avg_duration_fmt)
    
# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👨‍🎤 Artists", "💿 Albums", "🎼 Tracks", "🎵 Genres"])

with tab1:

    st.subheader("Top 10 Artists by No. Fans — by Musical Era")

# --- Let user choose era ---
period = st.radio(
    "Select Period:",
    ["Since 2000", "1980–1999", "1950–1979"],
    horizontal=True
)

# --- Build SQL WHERE clause dynamically ---
if period == "Since 2000":
    date_filter = "AlbumReleaseDate >= '2000-01-01'"
elif period == "1980–1999":
    date_filter = "AlbumReleaseDate BETWEEN '1980-01-01' AND '1999-12-31'"
else:  # 1950–1979
    date_filter = "AlbumReleaseDate BETWEEN '1950-01-01' AND '1979-12-31'"

# --- Query top artists for selected era ---
query = f"""
    SELECT ArtistName, MAX(ArtistNbFan) AS fans
    FROM deezer_table
    WHERE {date_filter}
    GROUP BY ArtistName
    ORDER BY fans DESC
    LIMIT 10
"""
top_artists = con.execute(query).df()

# --- Choose color dynamically based on period ---
color_map = {
    "Since 2000": "#1f77b4",    # blue
    "1980–1999": "#ff7f0e",     # orange
    "1950–1979": "#2ca02c"      # green
}

# --- Create chart ---
chart = (
    alt.Chart(top_artists)
    .mark_bar()
    .encode(
        x=alt.X("ArtistName:N", sort="-y", title="Artist"),
        y=alt.Y("fans:Q", title="No. Fans"),
        color=alt.value(color_map[period])
    )
    .properties(
        title=f"Top 10 Artists — {period}",
        width=700,
        height=400
    )
)

st.altair_chart(chart, use_container_width=True)


with tab2:
    
    # 1800-2028 period
    st.subheader("Albums Released per Year - 1800-2028 period")
    album = con.execute("""
        SELECT SUBSTRING(AlbumReleaseDate,1,4) AS year, COUNT(*) as album_count
        FROM deezer_table
        WHERE AlbumReleaseDate IS NOT NULL
          AND SUBSTRING(AlbumReleaseDate,1,4) ~ '^[0-9]{4}$'
          AND CAST(SUBSTRING(AlbumReleaseDate,1,4) AS INT) BETWEEN 1800 AND 2030
        GROUP BY year
        ORDER BY year
    """).df()
    st.line_chart(album.set_index("year"))

    #1950-2000 period
    st.subheader("Albums Released per Year - 1950-2000 period")
    album = con.execute("""
        SELECT SUBSTRING(AlbumReleaseDate,1,4) AS year, COUNT(*) as album_count
        FROM deezer_table
        WHERE AlbumReleaseDate IS NOT NULL
          AND SUBSTRING(AlbumReleaseDate,1,4) ~ '^[0-9]{4}$'
          AND CAST(SUBSTRING(AlbumReleaseDate,1,4) AS INT) BETWEEN 1950 AND 2000
        GROUP BY year
        ORDER BY year
    """).df()
    st.line_chart(album.set_index("year"))

with tab3:
    st.subheader("Top 20 artists - Track Popularity distribution")
    artist_list = tuple(top_per_fans["ArtistName"].tolist())

    track = f"""
        SELECT TrackRank, ArtistName
        FROM deezer_table
        WHERE TrackRank IS NOT NULL
          AND TrackRank BETWEEN 0 AND 400000
          AND ArtistName IN {artist_list}
    """
    track_df = con.execute(track).df()

    artist_chart = alt.Chart(track_df).mark_boxplot(extent="min-max").encode(
        x=alt.X("ArtistName:N", title="Artist"),
        y=alt.Y("TrackRank:Q", title="Track Rank (lower = more popular)"),
        color="ArtistName:N"
    ).properties(width=700, height=400)

    st.altair_chart(artist_chart, use_container_width=True)

with tab4:
    st. subheader("Genres Distribution")

    album_genre = con.execute("""
        SELECT AlbumGenreName, COUNT(*) as genre_count
        FROM deezer_table
        WHERE AlbumGenreName IS NOT NULL
          AND AlbumGenreName != ''
        GROUP BY AlbumGenreName
    """).df()

    album_chart = alt.Chart(album_genre).mark_bar().encode(
        x=alt.X("AlbumGenreName:N", sort="-y", title="Genre"),
        y=alt.Y("genre_count:Q", title="Albums"),
        color=alt.value("#0effc7")
    ).properties(width=700, height=400)

    st.altair_chart(album_chart, use_container_width=True)

