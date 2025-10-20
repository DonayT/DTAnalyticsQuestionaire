import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import json

def load_pitch_colors():
    try: 
        config_path = os.path.join('PitchColors.json')
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Pitch color load failed.")
        return {}

def create_pie_charts(pitch_usage):
    colors_map = load_pitch_colors()

    pitcher_id = pitch_usage['PitcherId']
    game_id = pitch_usage['GameId']
    total_pitches = pitch_usage['TotalPitches']

    pitch_keys = ['FF', 'SI', 'FC', 'CU', 'CH', 'SL', 'KC']

    labels = []
    sizes = []
    colors = []
    
    for k in pitch_keys:
        count = pitch_usage.get(k, 0)
        if count > 0:
            labels.append(k)
            # Calculate percentage of total pitches
            percentage = (count / total_pitches) * 100
            sizes.append(percentage)
            colors.append(colors_map.get(k, '#999999'))

    if not sizes:
        return

    fig, ax = plt.subplots(figsize=(6,6))
    plt.pie(
        sizes,
        labels = labels,
        autopct='%1.1f%%',
        startangle=90,
        counterclock=False
    )
    plt.title(f"Pitch Usage: Game {game_id} - Pitcher {pitcher_id}")

    out_dir = 'PitchUsageCharts'
    os.makedirs(out_dir, exist_ok=True)
    outfile = os.path.join(out_dir, f'pitch_usage_game{game_id}_pitcher{pitcher_id}.png')
    plt.savefig(outfile, bbox_inches='tight', dpi=150)
    plt.close(fig)

    print(pitch_usage)


def get_pitcher_data(games_dir='PitcherGameResults'):

    if not os.path.exists(games_dir):
        return

    for filename in os.listdir(games_dir):
        if filename.endswith('.csv'):
            game_file = os.path.join(games_dir, filename)

            # Extract game id from filename
            match = re.search(r'Game(\d+)', filename)
            game_id = int(match.group(1)) if match else 0

            df = pd.read_csv(game_file)

            for pitcher_id in df['PitcherId'].unique():
                pitch_usage_stats = df[df['PitcherId'] == pitcher_id]

                def to_int_safe(value):
                    try:
                        return int(value)
                    except (TypeError, ValueError):
                        return 0

                pitch_usage_stats = {
                    'GameId': game_id,
                    'PitcherId': to_int_safe(pitcher_id),
                    'TotalPitches': to_int_safe(pitch_usage_stats['TotalPitches'].iloc[0] if 'TotalPitches' in pitch_usage_stats.columns and not pitch_usage_stats['TotalPitches'].empty else 0),
                    'FF': to_int_safe(pitch_usage_stats['FF'].iloc[0] if 'FF' in pitch_usage_stats.columns and not pitch_usage_stats['FF'].empty else 0),
                    'SI': to_int_safe(pitch_usage_stats['SI'].iloc[0] if 'SI' in pitch_usage_stats.columns and not pitch_usage_stats['SI'].empty else 0),
                    'FC': to_int_safe(pitch_usage_stats['FC'].iloc[0] if 'FC' in pitch_usage_stats.columns and not pitch_usage_stats['FC'].empty else 0),
                    'CU': to_int_safe(pitch_usage_stats['CU'].iloc[0] if 'CU' in pitch_usage_stats.columns and not pitch_usage_stats['CU'].empty else 0),
                    'CH': to_int_safe(pitch_usage_stats['CH'].iloc[0] if 'CH' in pitch_usage_stats.columns and not pitch_usage_stats['CH'].empty else 0),
                    'SL': to_int_safe(pitch_usage_stats['SL'].iloc[0] if 'SL' in pitch_usage_stats.columns and not pitch_usage_stats['SL'].empty else 0),
                    'KC': to_int_safe(pitch_usage_stats['KC'].iloc[0] if 'KC' in pitch_usage_stats.columns and not pitch_usage_stats['KC'].empty else 0)
                }

                create_pie_charts(pitch_usage_stats)

def main():
    get_pitcher_data()

if __name__ == "__main__":
    main()

