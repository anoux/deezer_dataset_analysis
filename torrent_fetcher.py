import bencodepy
from pathlib import Path
from collections import Counter
import py7zr

# Step 1: Find out file names and sizes
torrent_file = "dataset.torrent"
with open(torrent_file, "rb") as f:
    torrent_data = bencodepy.decode(f.read())

files = torrent_data[b'info'].get(b'files')

if files:
    for f in files:
        path = b"/".join(f[b'path']).decode("utf-8")
        length = f[b'length']
        print(f"{path} ({length/1024/1024:.2f} MB)")
else:
    # Single-file torrent
    print(torrent_data[b'info'][b'name'].decode("utf-8"))

# Step 2: Download csv files within torrent file

import libtorrent as lt
import time

ses = lt.session()
ses.listen_on(6881, 6891)

# Load torrent
info = lt.torrent_info(torrent_file)
h = ses.add_torrent({'ti': info, 'save_path': './downloads'})

# Disable all files first
fs = info.files()
for i in range(fs.num_files()):
    h.file_priority(i, 0)

# Enable only CSV Datasets.7z
for i in range(fs.num_files()):
    if "CSV Datasets.7z" in fs.file_path(i):
        h.file_priority(i, 1)

print("Starting download...")
while not h.is_seed():
    s = h.status()
    print(f"{s.progress * 100:.2f}% complete, "
          f"{s.download_rate / 1000:.1f} kB/s down, "
          f"{s.upload_rate / 1000:.1f} kB/s up, "
          f"{s.num_peers} peers")
    time.sleep(2)

print("Download finished!")
# /Users/anx/Documents/deezer_analysis/downloads/MusicBrainz Tidal Spotify Deezer Dataset 06 July 2025/CSV Datasets.7z







'''
# Step 2: Extract file info
file_info = []
extensions = []

for f in files:
    path_parts = [p.decode() for p in f[b'path']]
    file_path = Path(*path_parts)
    size = f.get(b'length', 0)
    file_info.append({"file": str(file_path), "size": size})
    extensions.append(file_path.suffix.lower())

# Step 3: Basic analysis
total_files = len(file_info)
total_size = sum(f['size'] for f in file_info)
file_type_counts = Counter(extensions)

# Step 4: Print results
print(f"Total files: {total_files}")
print(f"Total size: {total_size / (1024**2):.2f} MB")
print("File types and counts:")
for ext, count in file_type_counts.items():
    print(f"  {ext or '[no extension]'}: {count}")

# Step 5: List files in 7z archive
archive_path = "dataset.7z"
with py7zr.SevenZipFile(archive_path, mode='r') as archive:
    file_list = archive.getnames()
    print(file_list)
    '''
