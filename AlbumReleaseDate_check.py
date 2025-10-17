import pandas as pd

with open("./extracted/deezer_flat.csv", 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if '2205-01-01' in line:
            print(f"Found on line {i}: {line.strip()}")
            break
