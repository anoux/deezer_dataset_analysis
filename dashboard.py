import duckdb
import streamlit as st
import altair as alt

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
st.metric("Avg Track Duration", avg_duration_fmt)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👨‍🎤 Artists", "💿 Albums", "🎼 Tracks", "🎵 Genres"])

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
