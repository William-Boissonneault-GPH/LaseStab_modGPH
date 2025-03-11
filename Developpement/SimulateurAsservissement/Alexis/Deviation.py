import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURABLE PARAMETERS ---
# Update the path with a raw string or use forward slashes to avoid escape issues
CSV_FILENAME = r'C:\Users\Alex_\OneDrive\Bureau\École\Design 2\Python\Essai2Asserv.csv'
TIME_COLUMN = 'Time'
TEMP_COLUMNS = ['Temp1', 'Temp2', 'Temp3', 'Temp4']
SETPOINT_COLUMN = 'Setpoint'

# Stability criteria for defining the permanent regime (in °C)
THRESHOLD = 0.2
STABILITY_DURATION = 6  # number of consecutive points within THRESHOLD

def find_setpoint_changes(df, setpoint_col):
    """
    Return a list of row indices where the setpoint changes.
    """
    changes = []
    sp_values = df[setpoint_col].values
    for i in range(1, len(sp_values)):
        if sp_values[i] != sp_values[i-1]:
            changes.append(i)
    return changes

def find_permanent_regime_time(df, temp_col, setpoint_col, start_idx, end_idx):
    """
    Within the index range [start_idx, end_idx), determine the time when the temperature 
    (temp_col) becomes "stable" around the setpoint (|temp - setpoint| <= THRESHOLD)
    for at least STABILITY_DURATION consecutive points.
    Returns the time value at which stability is first confirmed.
    """
    stable_count = 0
    for i in range(start_idx, end_idx):
        t = df[temp_col].iloc[i]
        sp = df[setpoint_col].iloc[i]
        if abs(t - sp) <= THRESHOLD:
            stable_count += 1
        else:
            stable_count = 0  # reset if the condition is broken
        if stable_count >= STABILITY_DURATION:
            return df[TIME_COLUMN].iloc[i]
    return None

def calculate_tau_for_temp4(df, start_idx, end_idx):
    """
    Calculates the time constant (tau) for Temp4 in the region between start_idx and end_idx.
    Uses the "63.2% rule": for a step change, tau is the time it takes for Temp4 to
    reach 63.2% of the difference between its initial value and the setpoint.
    If no step or crossing is found, returns None.
    """
    region = df.iloc[start_idx:end_idx]
    if region.empty:
        return None

    t0 = region[TIME_COLUMN].iloc[0]
    y0 = region['Temp4'].iloc[0]
    sp = region[SETPOINT_COLUMN].iloc[0]  # setpoint is assumed constant in the region

    # If there is no step change, return 0 (or you could choose to return None)
    if y0 == sp:
        return 0.0

    # Calculate the target value at 63.2% of the step change
    target = y0 + 0.632 * (sp - y0)
    
    # Determine the direction of the step (upward or downward)
    increasing = sp > y0

    prev_time = None
    prev_value = None
    for idx in region.index:
        current_time = df.at[idx, TIME_COLUMN]
        current_value = df.at[idx, 'Temp4']
        
        # Set the previous point if not already set
        if prev_value is None:
            prev_time, prev_value = current_time, current_value
            continue
        
        # For an increasing step, look for crossing above the target; for a decreasing step, below.
        if increasing:
            if prev_value < target <= current_value:
                # Linear interpolation to approximate the crossing time
                fraction = (target - prev_value) / (current_value - prev_value)
                interpolated_time = prev_time + fraction * (current_time - prev_time)
                return interpolated_time - t0
        else:
            if prev_value > target >= current_value:
                fraction = (prev_value - target) / (prev_value - current_value)
                interpolated_time = prev_time + fraction * (current_time - prev_time)
                return interpolated_time - t0

        prev_time, prev_value = current_time, current_value

    return None

def main():
    # 1. Read the CSV
    df = pd.read_csv(CSV_FILENAME)

    # 3. Detect setpoint changes
    change_indices = find_setpoint_changes(df, SETPOINT_COLUMN)
    # Add boundaries for the first and last region
    change_indices = [0] + change_indices + [len(df)]

    results = []
    for i in range(len(change_indices) - 1):
        start_idx = change_indices[i]
        end_idx = change_indices[i + 1]
        
        # Duration for which the setpoint remained constant
        region_duration = df[TIME_COLUMN].iloc[end_idx - 1] - df[TIME_COLUMN].iloc[start_idx]
        
        current_setpoint = df[SETPOINT_COLUMN].iloc[start_idx]

        # 4a. Full region standard deviations for Temp3 and Temp4 (deviation from setpoint)
        region_df = df.iloc[start_idx:end_idx]
        temp3_dev_region = region_df['Temp3'] - region_df[SETPOINT_COLUMN]
        temp4_dev_region = region_df['Temp4'] - region_df[SETPOINT_COLUMN]
        std_temp3_region = temp3_dev_region.std() if not temp3_dev_region.empty else None
        std_temp4_region = temp4_dev_region.std() if not temp4_dev_region.empty else None

        # 4b. Permanent regime detection for Temp3 and Temp4
        regime_start_3 = find_permanent_regime_time(df, 'Temp3', SETPOINT_COLUMN, start_idx, end_idx)
        regime_start_4 = find_permanent_regime_time(df, 'Temp4', SETPOINT_COLUMN, start_idx, end_idx)
        if regime_start_3 is not None and regime_start_4 is not None:
            regime_start_time = max(regime_start_3, regime_start_4)
        else:
            regime_start_time = None

        if regime_start_time is not None:
            stable_df = df[(df[TIME_COLUMN] >= regime_start_time) & (df.index < end_idx)]
            temp3_dev_stable = stable_df['Temp3'] - stable_df[SETPOINT_COLUMN]
            temp4_dev_stable = stable_df['Temp4'] - stable_df[SETPOINT_COLUMN]
            std_temp3_perm = temp3_dev_stable.std() if not temp3_dev_stable.empty else None
            std_temp4_perm = temp4_dev_stable.std() if not temp4_dev_stable.empty else None
            time_to_stable = regime_start_time - df[TIME_COLUMN].iloc[start_idx]
        else:
            std_temp3_perm = None
            std_temp4_perm = None
            time_to_stable = None

        # 4c. Calculate time constant (tau) for Temp4 using the 63.2% rule
        tau_temp4 = calculate_tau_for_temp4(df, start_idx, end_idx)

        results.append({
            'Setpoint': current_setpoint,
            'StartIndex': start_idx,
            'EndIndex': end_idx,
            'SetpointDuration': region_duration,
            'RegimeStartTime': regime_start_time,
            'TimeToStable': time_to_stable,
            'StdDev_Temp3_Region': std_temp3_region,
            'StdDev_Temp4_Region': std_temp4_region,
            'StdDev_Temp3_PermRegime': std_temp3_perm,
            'StdDev_Temp4_PermRegime': std_temp4_perm,
            'Tau_Temp4': tau_temp4
        })

    # 5. Print the results
    print("RESULTS PER SETPOINT REGION:")
    for r in results:
        print(f"Setpoint: {r['Setpoint']}")
        print(f"  StartIndex: {r['StartIndex']}, EndIndex: {r['EndIndex']}")
        print(f"  Duration of Setpoint: {r['SetpointDuration']} seconds")
        print(f"  Permanent Regime Start Time: {r['RegimeStartTime']}")
        print(f"  Time To Stable: {r['TimeToStable']} seconds")
        print(f"  StdDev (Temp3, Full Region): {r['StdDev_Temp3_Region']}")
        print(f"  StdDev (Temp4, Full Region): {r['StdDev_Temp4_Region']}")
        print(f"  StdDev (Temp3, Perm Regime): {r['StdDev_Temp3_PermRegime']}")
        print(f"  StdDev (Temp4, Perm Regime): {r['StdDev_Temp4_PermRegime']}")
        print(f"  Time Constant Tau for Temp4: {r['Tau_Temp4']} seconds")
        print("")

        
    # 2. Plot the temperatures and setpoint vs. time
    plt.figure(figsize=(10, 6))
    for col in TEMP_COLUMNS:
        plt.plot(df[TIME_COLUMN], df[col], label=col)
    plt.plot(df[TIME_COLUMN], df[SETPOINT_COLUMN], '--', label='Setpoint', color='black')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (°C)')
    plt.title('Temperature vs. Time')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()
