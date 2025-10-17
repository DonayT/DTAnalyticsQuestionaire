import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


def split_csv_by_gamepk(source_csv, output_dir):
    # Creates per-GamePk CSV files with header preserved
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Read the header from the source CSV
    try:
        with open(source_csv, 'r', newline='') as src:
            reader = csv.reader(src)
            header = next(reader)
    except FileNotFoundError:
        print(f"{source_csv} not found")
        return 0
    except StopIteration:
        return 0

    try:
        gamepk_idx = header.index('GamePk')
    except ValueError:
        print("Column 'GamePk' not found in CSV header")
        return 0

    # Group the rows by GamePk into a dictionary
    game_to_rows = {}
    with open(source_csv, 'r', newline='') as src:
        reader = csv.reader(src)
        next(reader, None)
        for row in reader:
            if gamepk_idx >= len(row):
                continue
            game_id = row[gamepk_idx]
            if game_id == '':
                continue
            game_to_rows.setdefault(game_id, []).append(row)

    # Write the per-GamePk CSV files
    files_written = 0
    for game_id, rows in game_to_rows.items():
        out_path = os.path.join(output_dir, f"game_{game_id}.csv")
        with open(out_path, 'w', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(header)
            writer.writerows(rows)
        files_written += 1
    return files_written

def sort_pitch_data(csv_file):
    # Open up active csv game file
    # Read the header from the source CSV
    try:
        with open(csv_file, 'r', newline='') as src:
            reader = csv.reader(src)
            header = next(reader)
    except FileNotFoundError:
        print(f"{csv_file} not found")
        return 0
    except StopIteration:
        return 0

    # Get the indices of the atBatNumber and pitchNumber columns
    try:
        atBatNumberIdx = header.index('AtBatNumber')
    except ValueError:
        print("Column 'AtBatNumber' not found in CSV header")
        return 0

    try:
        pitchNumberIdx = header.index('PitchNumber')
    except ValueError:
        print("Column 'pitchNumber' not found in CSV header")
        return 0

    # Collect all rows into a list
    rows = []
    with open(csv_file, 'r', newline='') as src:
        reader = csv.reader(src)
        next(reader, None)
        for row in reader:
            if row[atBatNumberIdx] == '':
                continue
            rows.append(row)

    # Sort rows by primary and optional secondary numeric keys
    rows.sort(key=lambda r: (int(r[atBatNumberIdx]), int(r[pitchNumberIdx])))

    # Write header and sorted rows back to the same file
    with open(csv_file, 'w', newline='') as out:
        writer = csv.writer(out)
        writer.writerow(header)
        writer.writerows(rows)

def main():
    input_name = 'AnalyticsQuestionnairePitchData.csv'

    # Split into per-GamePk files
    games_dir = 'gamesSorted'
    count = split_csv_by_gamepk(input_name, games_dir)
    print(f"Wrote {count} per-game CSV files to '{games_dir}'")

    # Sort the pitch data for each game
    for file in os.listdir(games_dir):
        sort_pitch_data(os.path.join(games_dir, file))



if __name__ == "__main__":
    main()