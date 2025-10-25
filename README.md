# Deezer Music Dashboard

Music seems to be an interesting topic to use in my data analysis learning process.  
This **[[Dataset](https://github.com/MusicMoveArr/Datasets)]** seemed to be quite challenging. I downloaded a torrent that contains deezer music dataset and parsed it. I got a csv file (49 data fields, 119.5 million records, 70 gb size) and did my best to get some insights from it.

## Steps I went through
1. Parsed a **[[torrent](https://github.com/MusicMoveArr/Datasets/blob/main/MusicBrainz%20Tidal%20Spotify%20Deezer%20Dataset%2006%20July%202025.torrent)]** containing deezer music dataset and extracted deezer dataset into a CSV file.
2. Due to csv size, used **[DuckDB](https://duckdb.org/)** right on the terminal to query and analyze the csv file with SQL:
   - First I created a database file by `con = duckdb.connect("deezer.db")`. The db database size is 30 gb, half of what I wanted to work with at the beggining.
   - As datatypes infere was giving several errors, I created an empty table and defined all headers and datatypes in advance (see table_headers.txt). Also, I had to covert some fields to VARCHAR (AlbumDuration, AlbumReleaseDate, TrackReleaseDate & TrackDuration) as they were giving errors. Then I populated the table with csv data like this:
   
      `COPY deezer_table FROM './extracted/deezer_flat.csv'  (AUTO_DETECT TRUE, HEADER TRUE);`

As I created a persistent databese, the longest step, which is populate the table with csv records has no longer to be done and access to database is just done by `.open FILENAME"` (FILENAME shall have an arbitrary extension, but .db or .duckdb are commonly used). Furthermore, DuckDB has strptime to parse strings into temporal types (on-the-fly conversion).

3. Built interactive dashboard with **[Streamlit](https://streamlit.io/)** to explore the data y get some insights.

Streamlit app on a browser can be easily executed by `streamlit run FILENAME.py`

## 📊 Features

### 👨‍🎤 Artists Tab
- **Top 20 Artists by Number of Fans**  
  Displays a bar chart ranking the most popular artists by their fan counts.
- **Top 20 Artists by Number of Albums**  
  Shows which artists have released the most albums.

### 💿 Albums Tab
- **Albums Released per Year (1800–2028)**  
  A full historical view of album release trends over time.
- **Albums Released per Year (1950–2000)**  
  A focused look at the modern music era.

### 🎼 Tracks Tab
- **Top 20 Artists – Track Popularity Distribution**  
  Displays a boxplot of track popularity (`TrackRank`) for the top artists.  
  (Note: lower rank values indicate higher popularity.)

### 🎵 Genres Tab
- **Genres Distribution**  
  Shows how many albums belong to each music genre, sorted from most to least represented.

## Rock and Disco analysis

I created an additional table to do more research within rock and disco tracks. From initial 119,500,260 rows and after excluding those with odd AlbumReleaseDate values, only 299 records compliant with conditions in the query below correspond to rock and disco, a minor fraction.

```sql
DROP TABLE IF EXISTS rock_and_disco;
CREATE TABLE rock_and_disco AS
· SELECT
· NULLIF(SUBSTRING(AlbumReleaseDate,1,4), '') AS year_str,
·   CASE
·     WHEN AlbumGenreName ILIKE '%rock%' THEN 'rock'
·     WHEN AlbumGenreName ILIKE '%disco%' THEN 'disco'
·     ELSE 'other'
·   END AS genre_norm,
·   COUNT(*) AS n_albums,
·   AVG(CASE WHEN TrackDurationSeconds IS NOT NULL THEN TrackDurationSeconds END) AS avg_track_seconds,
·   AVG(CASE WHEN TrackBPM IS NOT NULL THEN TrackBPM END) AS avg_bpm,
·   AVG(CASE WHEN TrackRank IS NOT NULL THEN TrackRank END) AS avg_rank,
·   COUNT(DISTINCT ArtistId) AS n_artists
· FROM deezer_table
· WHERE AlbumGenreName IS NOT NULL
·   AND AlbumGenreName != ''
‣   AND CAST(SUBSTRING(AlbumReleaseDate,1,4) AS INT) BETWEEN 1800 AND 2025
· GROUP BY year_str, genre_norm
· HAVING year_str IS NOT NULL;
```
