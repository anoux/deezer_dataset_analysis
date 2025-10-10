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
