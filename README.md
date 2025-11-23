# Deezer Music Dashboard
  
This project is a self-directed data analysis and visualization app built to explore and analyze a large dataset of Deezer music metadata.

## 🛠️ Technologies Used

- DuckDB — fast analytical SQL engine embedded in Python
- Streamlit — interactive web app framework
- Altair — declarative visualization library
- Python — orchestration, data manipulation, and formatting

I analysed this **[Dataset](https://github.com/MusicMoveArr/Datasets)** I found on Github. I downloaded a torrent file that contains deezer music dataset and parsed it. I got a csv file (49 data fields, 119.5 million records, 70 gb size) and did my best to get insights from it.

### Steps I went through
1. Parsed a **[torrent](https://github.com/MusicMoveArr/Datasets/blob/main/MusicBrainz%20Tidal%20Spotify%20Deezer%20Dataset%2006%20July%202025.torrent)** containing deezer music dataset and extracted deezer dataset into a CSV file.
2. Due to csv size, used **[DuckDB](https://duckdb.org/)** right on the terminal to query and analyze the csv file with SQL:
   - First I created a database by `con = duckdb.connect("deezer.db")`. So, from the initial 70 gb csv file I got a 30 gb database feasible to work with.
   - As datatypes infere was giving several errors, I created an empty table and defined all headers and datatypes in advance (see table_headers.txt). Also, I had to covert some fields to VARCHAR (AlbumDuration, AlbumReleaseDate, TrackReleaseDate & TrackDuration) as they were giving errors. Then I populated the table with csv data by:

      `COPY deezer_table FROM './extracted/deezer_flat.csv'  (AUTO_DETECT TRUE, HEADER TRUE);`

As I created a persistent databese, access to database is just done by `.open FILENAME"` (FILENAME shall have an arbitrary extension, but .db or .duckdb are commonly used). Furthermore, DuckDB has strptime to parse strings into temporal types (on-the-fly conversion).

3. Built interactive dashboard with **[Streamlit](https://streamlit.io/)** to explore the data y get some insights.

Display Streamlit app on a browser can be easily executed by `streamlit run FILENAME.py`

## 🚀 Project Overview

At a firt instance, I worked with these data fields

- Artists
- Albums
- Tracks
- Genres
- Release dates
- Popularity metrics such as number of fans and track rank

The dashboard provides interactive insights through KPIs, charts, and comparisons across time periods and categories.

## High-Level KPIs

The first section computes and displays aggregated metrics, including:

- Number of genres, artists, albums, and tracks
- Avg Artists per genre
- Avg Albums per artist
- Avg Tracks per album
- Average track duration
- Additional industry-level averages computed using nested SQL queries

<img width="643" height="402" alt="image" src="https://github.com/user-attachments/assets/bcb5c251-3a0c-4aad-ad13-cdb9256e58b1" />

These KPIs give a quick overview of the structure and richness of the dataset.

## 👨‍🎤 Tab 1 — Artists

This section includes multiple time-based comparisons of artist popularity.

Top 10 artists by number of fans during:

- 1950–1979 - Disco & Birth of rock ’n’ roll
- 1980–1999 - Pop explosion & Electronic beginnings
- 2000 onward - Genre fusion

Each period is visualized using Altair bar charts.
The dashboard also includes track popularity distribution (boxplots) for the top artists of the 1950–1979 period.

<img width="746" height="399" alt="image" src="https://github.com/user-attachments/assets/7031cddc-bb60-4df1-a342-c6dd8259da36" />

## 💿 Tab 2 — Albums & Artists Over Time

A time-series chart of album and artists counts:

This shows trends in music industry volume across decades and the jump aroun the 2000s is truly amazing.

<img width="820" height="507" alt="image" src="https://github.com/user-attachments/assets/a7a90d3e-9dca-4b3b-bc6e-0369dd4a54ab" />

## 🎼 Tab 3 — Track Popularity

A distribution analysis of track rankings (0–400k range) for the top artists (1950–1979), using Altair boxplots to compare popularity variation across artists.

<img width="724" height="472" alt="image" src="https://github.com/user-attachments/assets/8b12915b-e1ba-4a3b-bc23-b646cf711cdd" />

## 🎵 Tab 4 — Genre Distribution

A global breakdown of albums by genre, built with:

Grouped SQL aggregations

A category-sorted Altair bar chart

<img width="735" height="442" alt="image" src="https://github.com/user-attachments/assets/1027bfe7-395c-4f26-b827-7cb0c402fdd3" />

This provides insight into which genres dominate the catalogue.
