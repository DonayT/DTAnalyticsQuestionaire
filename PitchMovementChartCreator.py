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


def create_movement_charts(all_pitches_data, pitcher_id, game_id):

    colors_map = load_pitch_colors()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Get unique pitch types and their colors for legend
    unique_pitch_types = list(set(pitch_data['PitchType'] for pitch_data in all_pitches_data))
    
    # Plot all pitches with different colors for each pitch type
    for pitch_data in all_pitches_data:
        pitch_type = pitch_data['PitchType']
        horizontal_break_inches = pitch_data['TrajectoryHorizontalBreak'] * 12
        vertical_break_inches = pitch_data['TrajectoryVerticalBreakInduced'] * 12
        
        point_color = colors_map.get(pitch_type, '#999999')
        
        ax.scatter(horizontal_break_inches, vertical_break_inches, 
                   c=point_color, s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
    

    legend_elements = []
    for pitch_type in unique_pitch_types:
        color = colors_map.get(pitch_type, '#999999')
        legend_elements.append(plt.scatter([], [], c=color, s=100, label=pitch_type, 
                                         edgecolors='black', linewidth=0.5))
    
    ax.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add labels and title
    ax.set_xlabel('Trajectory Horizontal Break (inches)', fontsize=12)
    ax.set_ylabel('Trajectory Vertical Break Induced (inches)', fontsize=12)
    ax.set_title(f'Pitch Movement: Game {game_id} - Pitcher {pitcher_id}', fontsize=14)
    
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax.set_xlim(-20, 20)
    ax.set_ylim(-20, 20)
    ax.set_aspect('equal', adjustable='box')
    
    out_dir = 'PitchMovementCharts'
    os.makedirs(out_dir, exist_ok=True)
    outfile = os.path.join(out_dir, f'pitch_movement_game{game_id}_pitcher{pitcher_id}.png')
    plt.savefig(outfile, bbox_inches='tight', dpi=150)
    plt.close(fig)


def get_pitcher_data(games_dir='PitcherMovement'):

    if not os.path.exists(games_dir):
        return

    for filename in os.listdir(games_dir):
        if filename.endswith('.csv'):
            game_file = os.path.join(games_dir, filename)

            match = re.search(r'Pitcher(\d+)MetricsGame(\d+)', filename)
            pitcher_id = int(match.group(1)) if match else 0
            game_id = int(match.group(2)) if match else 0

            df = pd.read_csv(game_file)

            def to_float_safe(value):
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return 0.0

            def to_int_safe(value):
                try:
                    return int(value)
                except (TypeError, ValueError):
                    return 0

            # Collect all pitch data from this file
            all_pitches_data = []
            
            for pitch_id in df['PitchID'].unique():
                pitch_movement_data = df[df['PitchID'] == pitch_id]

                pitch_data = {
                    'GameId': game_id,
                    'PitcherId': to_int_safe(pitcher_id),
                    'PitchType': pitch_movement_data['PitchType'].iloc[0] if 'PitchType' in pitch_movement_data.columns and not pitch_movement_data['PitchType'].empty else '',
                    'TrajectoryHorizontalBreak': to_float_safe(pitch_movement_data['TrajectoryHorizontalBreak'].iloc[0] if 'TrajectoryHorizontalBreak' in pitch_movement_data.columns and not pitch_movement_data['TrajectoryHorizontalBreak'].empty else 0),
                    'TrajectoryVerticalBreakInduced': to_float_safe(pitch_movement_data['TrajectoryVerticalBreakInduced'].iloc[0] if 'TrajectoryVerticalBreakInduced' in pitch_movement_data.columns and not pitch_movement_data['TrajectoryVerticalBreakInduced'].empty else 0),
                }
                
                all_pitches_data.append(pitch_data)

            # Create one chart for all pitches in this file
            if all_pitches_data:
                create_movement_charts(all_pitches_data, pitcher_id, game_id)

def main():
    get_pitcher_data()

if __name__ == "__main__":
    main()

