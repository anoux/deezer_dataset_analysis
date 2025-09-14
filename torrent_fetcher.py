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
    