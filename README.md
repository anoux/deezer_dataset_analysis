# Exploring Music Metadata with DuckDB

I’ve always found music fascinating, so I thought it would be interesting topic to use in my data analysis learning process.  
This **[[Dataset](https://github.com/MusicMoveArr/Datasets)]** seemed to be quite challenging and I choose it for this little project of mine
I downloaded a torrent and parsed the metadata, got a csv file (49 data fields, 119.5 million records, 70 gb size), and did my best to  insights I could get from it.

## What I Did
1. Parsed a **[[torrent](https://github.com/MusicMoveArr/Datasets/blob/main/MusicBrainz%20Tidal%20Spotify%20Deezer%20Dataset%2006%20July%202025.torrent)]** containing music files and extracted deezer dataset into a CSV file.
2. Due to csv size, I used **[DuckDB](https://duckdb.org/)** right on the terminal to query and analyze the csv file with SQL
   First I created a database file by con = duckdb.connect("deezer.db") 
   As datatypes infere was giving several errors, I created an empty table and defined all headers and datatypes (see table_headers.txt). Also, I had to covert some fields to VARCHAR (AlbumDuration, AlbumReleaseDate, TrackReleaseDate & TrackDuration). Then I populated the table with csv data like this:
   
   COPY deezer_table 
   FROM './extracted/deezer_flat.csv' 
   (AUTO_DETECT TRUE, HEADER TRUE);

As I created a persistent databese, now I can worked 
3. Built interactive dashboards with **[Streamlit](https://streamlit.io/)** to explore:
   - Artists and their fan counts  
   - Album releases over time  
   - Track-level details like duration, rank, BPM, and explicitness  

## Some Insights
- Which artists have the most albums or fans  
- How album releases are distributed by year  
- How track durations vary across the dataset  
- A quick look at track "energy" via BPM and gain