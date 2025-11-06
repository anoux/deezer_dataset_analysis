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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["👨‍🎤 Artists", "💿 Albums", "🎼 Tracks", "🎵 Genres", "🎸 Rock & Disco 🪩"])

with tab1:

    # as per fans
    st.subheader("Top 20 Artists by Number of Fans")
    top_per_fans = con.execute("""
        SELECT ArtistName, MAX(ArtistNbFan) as fans
        FROM deezer_table
        GROUP BY ArtistName
        ORDER BY fans DESC
        LIMIT 20
    """).df()

    fans_chart = alt.Chart(top_per_fans).mark_bar().encode(
        x=alt.X("ArtistName:N", sort="-y", title="Artist"),
        y=alt.Y("fans:Q", title="Fans"),
        color=alt.value("#1f77b4")
    ).properties(width=700, height=400)

    st.altair_chart(fans_chart, use_container_width=True)

    # as per albums
    st.subheader("Top 20 Artists by Number of Albums")

    top_per_albums = con.execute("""
        SELECT ArtistName, COUNT(DISTINCT AlbumId) AS albums
        FROM deezer_table
        GROUP BY ArtistName
        ORDER BY Albums DESC
        LIMIT 20
    """).df()

    albums_chart = alt.Chart(top_per_albums).mark_bar().encode(
        x=alt.X("ArtistName:N", sort="-y", title="Artist"),
        y=alt.Y("albums:Q", title="Albums"),
        color=alt.value("#ff7f0e")
    ).properties(width=700, height=400)

    st.altair_chart(albums_chart, use_container_width=True)

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

with tab5:
    st. subheader("Rock & Disco")
    rd_albums = con.execute("""
        SELECT CAST(year_str AS INT) AS year, genre_norm, SUM(n_albums) AS albums
        FROM rock_and_disco
        WHERE genre_norm IN ('rock','disco')
        AND CAST(year_str AS INT) BETWEEN 1980 AND 2025
        GROUP BY year, genre_norm
        ORDER BY year
    """).df()
    
    rd_chart = alt.Chart(rd_albums).mark_bar().encode(
        x=alt.X("year:N", sort="-y", title="Year"),
        y=alt.Y("albums:Q", title="Albums"),
        color=alt.Color("genre_norm:N", title="Genre")
    ).properties(width=700, height=400)
    
    st.altair_chart(rd_chart, use_container_width=True)
    
    st.subheader("BPM, duration & popularity")
    comp = con.execute("""
        SELECT CAST(year_str AS INT) AS year, genre_norm,
        AVG(avg_bpm) AS avg_bpm,
        AVG(avg_track_seconds) AS avg_seconds,
        AVG(avg_rank) AS avg_rank
        FROM rock_and_disco
        WHERE genre_norm IN ('rock','disco')
        GROUP BY year, genre_norm
        ORDER BY year                   
    """).df()

    comp_melted = comp.melt(
    id_vars=["year", "genre_norm"],
    value_vars=["avg_bpm", "avg_seconds", "avg_rank"],
    var_name="feature",
    value_name="value"
    )

    y_scales = {
    "avg_bpm": [0, 100],
    "avg_seconds": [0, 500],
    "avg_rank": [0, 350000]
}

charts = []

for feature, ydomain in y_scales.items():
    subset = comp_melted[comp_melted["feature"] == feature]

    chart = (
        alt.Chart(subset)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y(
                "value:Q",
                title=feature.replace("avg_", "").replace("_", " ").title(),
                scale=alt.Scale(domain=ydomain)  # 👈 custom Y-axis
            ),
            color=alt.Color("genre_norm:N", title="Genre"),
        )
        .properties(width=700, height=200, title=f"{feature.title()} over Time")
    )

    charts.append(chart)

# Combine vertically
final_chart = alt.vconcat(*charts)
st.altair_chart(final_chart, use_container_width=True)