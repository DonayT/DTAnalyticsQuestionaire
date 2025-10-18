import csv
import os
import pandas as pd
import numpy as np
from collections import defaultdict

def calculate_pitcher_stats(game_file, game_id):

    df = pd.read_csv(game_file)
    
    # Group by pitcher to calculate individual stats
    pitcher_stats = {}
    
    for pitcher_id in df['PitcherId'].unique():
        if pd.isna(pitcher_id):
            continue
            
        pitcher_data = df[df['PitcherId'] == pitcher_id]

        pitcher_team = 1 if pitcher_data['IsTop'].iloc[0] == 1 else 2
        pitcher_hand = pitcher_data['PitcherHand'].iloc[0] if not pitcher_data['PitcherHand'].empty else 'Unknown'
        outs_recorded = 0
        hits_1b = 0
        hits_2b = 0
        hits_3b = 0
        hits_hr = 0
        strikeouts = 0
        walks = 0
        total_batters_faced = len(pitcher_data['AtBatNumber'].unique())
        total_pitches = 0
        strikes = 0
        last_pitch_number = None
        
        # Count pitches by type
        pitch_type_counts = defaultdict(int)
        pitch_type_strikes = defaultdict(int)
        
        # Process each pitch
        for _, pitch in pitcher_data.iterrows():
            pitch_call = pitch['PitchCall']
            pitch_type = pitch['PitchType']
            pitch_number = pitch['PitchNumber']
            
            # Only count actual pitches (exclude pickoffs, stolen bases)
            if pd.notna(pitch_number) and pitch_number != last_pitch_number:
                total_pitches += 1
                last_pitch_number = pitch_number
                
                # Count strikes
                if pitch_call in ['called_strike', 'swinging_strike', 'foul_tip', 'field_out', 'foul', 'single', 'double', 'triple', 'home_run', 'grounded_into_double_play']:
                    strikes += 1
                    if pd.notna(pitch_type):
                        pitch_type_strikes[pitch_type] += 1
                
                # Count pitch types
                if pd.notna(pitch_type):
                    pitch_type_counts[pitch_type] += 1
            

            # Count results
            if pitch_call in ['single']:
                hits_1b += 1
            elif pitch_call in ['double']:
                hits_2b += 1
            elif pitch_call in ['triple']:
                hits_3b += 1
            elif pitch_call in ['home_run']:
                hits_hr += 1
            
            if pitch_call == 'strikeout':
                strikeouts += 1
                outs_recorded += 1
            elif pitch_call == 'walk':
                walks += 1
            elif pitch_call == 'field_out':
                outs_recorded += 1
            elif pitch_call == 'force_out':
                outs_recorded += 1
            elif pitch_call == 'grounded_into_double_play':
                outs_recorded += 2
            

            innings_pitched = round(outs_recorded / 3.0, 2)
        
        # Calculate derived stats
        total_hits = hits_1b + hits_2b + hits_3b + hits_hr
        baa = total_hits / total_batters_faced if total_batters_faced > 0 else 0
        whip = (total_hits + walks) / innings_pitched if innings_pitched > 0 else 0
        strike_percentage = strikes / total_pitches if total_pitches > 0 else 0
        
        # Calculate strikeout percentages for each pitch type
        pitch_type_k_percentages = {}
        for pitch_type in pitch_type_counts:
            if pitch_type_counts[pitch_type] > 0:
                pitch_type_k_percentages[f"{pitch_type}_K%"] = (pitch_type_strikes[pitch_type] / pitch_type_counts[pitch_type]) * 100
            else:
                pitch_type_k_percentages[f"{pitch_type}_K%"] = 0
        
        # Store pitcher stats
        pitcher_stats[pitcher_id] = {
            'PitcherId': pitcher_id,
            'PitcherTeam': pitcher_team,
            'PitcherHand': pitcher_hand,
            'OutsRecorded': outs_recorded,
            'InningsPitched': round(innings_pitched, 2),
            '1B': hits_1b,
            '2B': hits_2b,
            '3B': hits_3b,
            'HR': hits_hr,
            'Strikeouts': strikeouts,
            'Walks': walks,
            'TotalBattersFaced': total_batters_faced,
            'BAA': round(baa, 3),
            'WHIP': round(whip, 3),
            'TotalPitches': total_pitches,
            'Strikes': strikes,
            'StrikePercentage': round(strike_percentage, 3),
            'FF': pitch_type_counts.get('FF', 0),
            'FF_K%': round(pitch_type_k_percentages.get('FF_K%', 0), 1),
            'SI': pitch_type_counts.get('SI', 0),
            'SI_K%': round(pitch_type_k_percentages.get('SI_K%', 0), 1),
            'FC': pitch_type_counts.get('FC', 0),
            'FC_K%': round(pitch_type_k_percentages.get('FC_K%', 0), 1),
            'CU': pitch_type_counts.get('CU', 0),
            'CU_K%': round(pitch_type_k_percentages.get('CU_K%', 0), 1),
            'CH': pitch_type_counts.get('CH', 0),
            'CH_K%': round(pitch_type_k_percentages.get('CH_K%', 0), 1),
            'SL': pitch_type_counts.get('SL', 0),
            'SL_K%': round(pitch_type_k_percentages.get('SL_K%', 0), 1),
            'KC': pitch_type_counts.get('KC', 0),
            'KC_K%': round(pitch_type_k_percentages.get('KC_K%', 0), 1)
        }
    
    return pitcher_stats

def calculate_pitcher_movement(game_file, game_id):
    # Read the CSV file
    df = pd.read_csv(game_file)
    
    # Get all unique pitcher IDs
    pitcher_ids = df['PitcherId'].unique()
    
    # For each pitcher, call the CSV generator
    for pitcher_id in pitcher_ids:
        if pd.isna(pitcher_id):
            continue
        
        # Create pitcher-specific data dictionary
        pitcher_data = {
            'PitchID': df[df['PitcherId'] == pitcher_id]['PitchId'].tolist(),
            'PitcherHand': df[df['PitcherId'] == pitcher_id]['PitcherHand'].iloc[0],
            'PitchType': df[df['PitcherId'] == pitcher_id]['PitchType'].tolist(),
            'ReleaseSpeed': df[df['PitcherId'] == pitcher_id]['ReleaseSpeed'].tolist(),
            'TrajectoryHorizontalBreak': df[df['PitcherId'] == pitcher_id]['TrajectoryHorizontalBreak'].tolist(),
            'TrajectoryVerticalBreakInduced': df[df['PitcherId'] == pitcher_id]['TrajectoryVerticalBreakInduced'].tolist(),
            'ReleasePositionX': df[df['PitcherId'] == pitcher_id]['ReleasePositionX'].tolist(),
            'ReleasePositionZ': df[df['PitcherId'] == pitcher_id]['ReleasePositionZ'].tolist()
        }
        
        # Call the CSV generator for this pitcher
        create_pitcher_metrics_csv(game_file, game_id, pitcher_id, pitcher_data)
    
    return pitcher_data

def create_pitcher_results_csv(game_file, game_id, output_dir='PitcherGameResults'):

    os.makedirs(output_dir, exist_ok=True)
    
    pitcher_stats = calculate_pitcher_stats(game_file, game_id)
    
    headers = [
        'PitcherId', 'PitcherTeam', 'PitcherHand', 'OutsRecorded', 'InningsPitched', '1B', '2B', '3B', 'HR',
        'Strikeouts', 'Walks', 'TotalBattersFaced', 'BAA', 'WHIP', 'TotalPitches', 'Strikes',
        'StrikePercentage', 'FF', 'FF_K%', 'SI', 'SI_K%', 'FC', 'FC_K%', 'CU', 'CU_K%',
        'CH', 'CH_K%', 'SL', 'SL_K%', 'KC', 'KC_K%'
    ]
    
    output_filename = f"PitcherResultsGame{game_id}.csv"
    output_path = os.path.join(output_dir, output_filename)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        
        for pitcher_id, stats in pitcher_stats.items():
            writer.writerow(stats)
    
    return output_path

def create_pitcher_metrics_csv(game_file, game_id, pitcher_id, pitcher_data, output_dir='PitcherMovement'):
    
    os.makedirs(output_dir, exist_ok=True)

    headers = [
        'PitchID', 'PitcherHand', 'PitchType', 'ReleaseSpeed', 'TrajectoryHorizontalBreak', 
        'TrajectoryVerticalBreakInduced', 'ReleasePositionX', 'ReleasePositionZ'
    ]

    output_filename = f"Pitcher{pitcher_id}MetricsGame{game_id}.csv"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()

        # Write each pitch as a row
        for i in range(len(pitcher_data['PitchID'])):
            row = {
                'PitchID': pitcher_data['PitchID'][i],
                'PitcherHand': pitcher_data['PitcherHand'],
                'PitchType': pitcher_data['PitchType'][i],
                'ReleaseSpeed': pitcher_data['ReleaseSpeed'][i],
                'TrajectoryHorizontalBreak': pitcher_data['TrajectoryHorizontalBreak'][i],
                'TrajectoryVerticalBreakInduced': pitcher_data['TrajectoryVerticalBreakInduced'][i],
                'ReleasePositionX': pitcher_data['ReleasePositionX'][i],
                'ReleasePositionZ': pitcher_data['ReleasePositionZ'][i]
            }
            writer.writerow(row)

    return output_path


def process_all_games(games_dir='gamesSorted'):

    if not os.path.exists(games_dir):
        print(f"Directory {games_dir} does not exist")
        return
    
    # Process each game file
    for filename in os.listdir(games_dir):
        if filename.endswith('.csv'):
            # Extract game ID from filename (e.g., 'game_1.csv' -> '1')
            game_id = filename.replace('game_', '').replace('.csv', '')
            
            game_file = os.path.join(games_dir, filename)
            
            try:
                create_pitcher_results_csv(game_file, game_id)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

            try: 
                calculate_pitcher_movement(game_file, game_id)
            except Exception as e:
                print(f"Error processing pitcher movement data")

def main():
    process_all_games()

if __name__ == "__main__":
    main()
