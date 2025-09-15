# Exploring Music Metadata with DuckDB

I’ve always found music fascinating, so I thought it would be an interesting topic to use in my data analysis learning process.  
This **[[Dataset](https://github.com/MusicMoveArr/Datasets)]** seemed to be quite challenging. I downloaded a torrent that contains deezer music dataset and parsed it. I got a csv file (49 data fields, 119.5 million records, 70 gb size) and did my best to get some insights from it.

## Steps I went through
1. Parsed a **[[torrent](https://github.com/MusicMoveArr/Datasets/blob/main/MusicBrainz%20Tidal%20Spotify%20Deezer%20Dataset%2006%20July%202025.torrent)]** containing deezer music dataset and extracted deezer dataset into a CSV file.
2. Due to csv size, used **[DuckDB](https://duckdb.org/)** right on the terminal to query and analyze the csv file with SQL:
   - First I created a database file by `code` con = duckdb.connect("deezer.db") `code`
   - As datatypes infere was giving several errors, I created an empty table and defined all headers and datatypes in advance (see table_headers.txt). Also, I had to covert some fields to VARCHAR (AlbumDuration, AlbumReleaseDate, TrackReleaseDate & TrackDuration) as they were giving errors. Then I populated the table with csv data like this:
   
      `code`
      COPY deezer_table 
      FROM './extracted/deezer_flat.csv' 
      (AUTO_DETECT TRUE, HEADER TRUE);
      `code`

As I created a persistent databese, the longest step, which is populate the table with csv records has no longer to be done and access to database is just done by `code` .open FILENAME" `code` (FILENAME shall have an arbitrary extension, but .db or .duckdb are commonly used).

3. Built interactive dashboards with **[Streamlit](https://streamlit.io/)** to explore:
   - Artists and their fan counts  
   - Album releases over time  
   - Track-level details like duration, rank, BPM, and explicitness

   Streamlit app on a browser can be easily executed by `code` streamlit run FILENAME.py `code`

## Some Insights
- Which artists have the most albums or fans  
- How album releases are distributed by year  
- How track durations vary across the dataset  
- A quick look at track "energy" via BPM and gain

