# Exploring Music Metadata with DuckDB

I’ve always found music fascinating, so I thought it would be interesting to explore it a bit more closely.  
By coincidence, I found out this 70gb **[[Dataset](https://github.com/MusicMoveArr/Datasets)] ()**
I downloaded a torrent and parsed the metadata (artist, album, release date, track info, etc.), and then see what kind of insights I could get from it.

## What I Did
1. Parsed a torrent containing music files and extracted metadata into a CSV file  
2. Used **[DuckDB](https://duckdb.org/)** to query and analyze the data efficiently with SQL
3. Built interactive dashboards with **[Streamlit](https://streamlit.io/)** to explore:
   - Artists and their fan counts  
   - Album releases over time  
   - Track-level details like duration, rank, BPM, and explicitness  

## Some Insights
- Which artists have the most albums or fans  
- How album releases are distributed by year  
- How track durations vary across the dataset  
- A quick look at track "energy" via BPM and gain