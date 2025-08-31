import py7zr
import pandas as pd

archive_path = "./downloads/CSV Datasets.7z"

# Extract deezer CSV
with py7zr.SevenZipFile(archive_path, mode='r') as archive:
    archive.extract(targets=['deezer_flat.csv'], path='./extracted')

import sqlite3

# Load CSV in chunks and insert into SQLite
con = sqlite3.connect("deezer.db")
chunks = pd.read_csv("./extracted/deezer_flat.csv", chunksize=100000)

for chunk in chunks:
    chunk.to_sql("tracks", con, if_exists="append", index=False)

# Query poc
df = pd.read_sql("SELECT * FROM tracks LIMIT 5", con)
print(df)