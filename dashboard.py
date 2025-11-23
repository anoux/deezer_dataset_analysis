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

    st.subheader("Top 10 Artists by No. Fans — Three periods")

    col1, col2, col3 = st.columns(3)

    #-- Top 10 artists during 1950-1979 ---
    top_1950_1979 = con.execute("""
        SELECT ArtistName, MAX(ArtistNbFan) AS fans
        FROM deezer_table
        WHERE AlbumReleaseDate BETWEEN '1950-01-01' AND '1979-12-31'
        GROUP BY ArtistName
        ORDER BY fans DESC
        LIMIT 10
    """).df()

    chart_1 = alt.Chart(top_1950_1979).mark_bar().encode(
        x=alt.X("ArtistName:N", sort="-y", title=""),
        y=alt.Y("fans:Q", title="No. Fans"),
        color=alt.value("#1f77b4")
    ).properties(
        title="During 1950-1979",
        width=350,
        height=400
    )

    # --- Top 10 artists during 1980-1999 ---
    top_1980_1999 = con.execute("""
        SELECT ArtistName, MAX(ArtistNbFan) AS fans
        FROM deezer_table
        WHERE AlbumReleaseDate BETWEEN '1980-01-01' AND '1999-12-31'
        GROUP BY ArtistName
        ORDER BY fans DESC
        LIMIT 10
    """).df()

    chart_2 = alt.Chart(top_1980_1999).mark_bar().encode(
        x=alt.X("ArtistName:N", sort="-y", title=""),
        y=alt.Y("fans:Q", title="No. Fans"),
        color=alt.value("#188f22")
    ).properties(
        title="During 1980-1999",
        width=350,
        height=400
    )

    # --- Top 10 artists form 2000 onward---
    top_since_2000 = con.execute("""
        SELECT ArtistName, MAX(ArtistNbFan) AS fans
        FROM deezer_table
        WHERE AlbumReleaseDate >= '2000-01-01'
        GROUP BY ArtistName
        ORDER BY fans DESC
        LIMIT 10
    """).df()

    chart_3 = alt.Chart(top_since_2000).mark_bar().encode(
        x=alt.X("ArtistName:N", sort="-y", title=""),
        y=alt.Y("fans:Q", title="No. Fans"),
        color=alt.value("#ff7f0e")
    ).properties(
        title="From 2000 onward",
        width=350,
        height=400
    )

    # --- Display charts side by side ---
    with col1:
        st.altair_chart(chart_1, use_container_width=True)

    with col2:
        st.altair_chart(chart_2, use_container_width=True)

    with col3:
        st.altair_chart(chart_3, use_container_width=True)


with tab2:
    
    # 1800-2025 period - albums and artists per year

    st.subheader("Artists & Albums per Year – 1800–2025")

    df = con.execute("""
        SELECT
            SUBSTRING(AlbumReleaseDate,1,4) AS year,
            COUNT(DISTINCT ArtistId) AS artist_count,
            COUNT(DISTINCT AlbumId) AS album_count
        FROM deezer_table
        WHERE AlbumReleaseDate IS NOT NULL
        AND SUBSTRING(AlbumReleaseDate,1,4) ~ '^[0-9]{4}$'
        AND CAST(SUBSTRING(AlbumReleaseDate,1,4) AS INT) BETWEEN 1800 AND 2025
        GROUP BY year
        ORDER BY year
    """).df()

    # reshape for altair long format
    df_long = df.melt(
        id_vars="year",
        value_vars=["artist_count", "album_count"],
        var_name="metric",
        value_name="count"
    )

    # pretty names
    df_long["metric"] = df_long["metric"].map({
        "artist_count": "Artists",
        "album_count": "Albums"
    })

    chart = alt.Chart(df_long).mark_line().encode(
        x=alt.X(
            "year:O",                # treat years as ordered categories
            title="Year",
            axis=alt.Axis(
                labelAngle=-90,
                labelOverlap="parity",
                format="d",
                tickCount=20          # adjust density of labels
            ),
            sort="ascending"
        ),
        y=alt.Y("count:Q", title="Count"),
        color=alt.Color(
            "metric:N",
            title="Metric",
            scale=alt.Scale(scheme="category10")
        )
    ).properties(
        width=900,
        height=450,
        title="Number of Artists & Albums per Year (1800–2025)"
    )

    st.altair_chart(chart, use_container_width=True)



with tab3:
    st.subheader("Top 10 artists during 1950-1979 - Track Popularity distribution")
    
    artist_list = tuple(top_1950_1979["ArtistName"].tolist())

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
    st.subheader("Genres Distribution")

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

    st.subheader("No. Albums for most popular Genres Over Time (1800–2025)")

    selected_genres = (
    'pop', 'rap/hiphop', 'electro', 'klassiek',
    'jazz', 'alternative', 'rock', 'disco'
    )

    genre_time = con.execute(f"""
        SELECT 
            CAST(SUBSTRING(AlbumReleaseDate, 1, 4) AS INT) AS year,
            LOWER(AlbumGenreName) AS genre,
            COUNT(*) AS album_count
        FROM deezer_table
        WHERE AlbumReleaseDate IS NOT NULL
          AND AlbumGenreName IS NOT NULL
          AND AlbumGenreName != ''
          AND AlbumGenreName IN {selected_genres}
          AND SUBSTRING(AlbumReleaseDate, 1, 4) ~ '^[0-9]{4}$'
          AND CAST(SUBSTRING(AlbumReleaseDate, 1, 4) AS INT) BETWEEN 1800 AND 2025
        GROUP BY year, genre
        ORDER BY year, genre
    """).df()

    genre_chart = alt.Chart(genre_time).mark_line().encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("album_count:Q", title="Albums Released"),
        color=alt.Color("genre:N", title="Genre")
    ).properties(
        width=800,
        height=450,
        title="Albums per Genre per Year (1800–2025)"
    )

    st.altair_chart(genre_chart, use_container_width=True)

