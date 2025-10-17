import csv
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

def get_pitcher_results(game_file):
    # Open up active csv game file

    
    with open(game_file, 'r', newline='') as src:
        reader = csv.reader(src)
        header = next(reader)
        for row in reader:
            if row[header.index('Pitcher')] == '':
                continue
            pitcher = row[header.index('Pitcher')]

def main():
    # For each game, collect the pitcher's results
    games_dir = 'gamesSorted'
    for file in os.listdir(games_dir):
        pitcher_dir = f"pitcherData_{os.path.splitext(file)[0]}"
        get_pitcher_results(os.path.join(games_dir, file))



if __name__ == "__main__":
    main()