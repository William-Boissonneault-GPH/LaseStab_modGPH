import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURABLE PARAMETERS ---
CSV_FILENAME = 'Developpement\SimulateurAsservissement\Alexis\Essai2Asserv.csv'
TIME_COLUMN = 'Time'
TEMP_COLUMNS = ['Temp1', 'Temp2', 'Temp3', 'Temp4']
SETPOINT_COLUMN = 'Setpoint'

# Instead of a fixed threshold, we now require the value to be within ±5% of the setpoint.
STABILITY_DURATION = 10  # number of consecutive points required

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

def find_settling_time(df, temp_col, setpoint_col, start_idx, end_idx):
    """
    Determines the time when the temperature (temp_col) is within ±5% of the setpoint.
    It requires that the condition holds for STABILITY_DURATION consecutive samples.
    Returns the time (from the Time column) at which this is first satisfied.
    """
    stable_count = 0
    for i in range(start_idx, end_idx):
        t = df[temp_col].iloc[i]
        sp = df[setpoint_col].iloc[i]
        # Check if t is within 95% to 105% of sp.
        if (t >= 0.95 * sp) and (t <= 1.05 * sp):
            stable_count += 1
        else:
            stable_count = 0  # reset count if condition fails

        if stable_count >= STABILITY_DURATION:
            return df[TIME_COLUMN].iloc[i]
    return None

def calculate_tau_for_temp4(df, start_idx, end_idx):
    """
    Calculates the time constant (tau) for Temp4 in the region between start_idx and end_idx.
    Uses the "63.2% rule": tau is the time it takes for Temp4 to reach 63.2% of the step change
    from its initial value (y0) to the setpoint.
    """
    region = df.iloc[start_idx:end_idx]
    if region.empty:
        return None

    t0 = region[TIME_COLUMN].iloc[0]
    y0 = region['Temp4'].iloc[0]
    sp = region[SETPOINT_COLUMN].iloc[0]  # constant setpoint in the region

    if y0 == sp:
        return 0.0

    # 63.2% target value
    target = y0 + 0.632 * (sp - y0)
    increasing = sp > y0

    prev_time = None
    prev_value = None
    for idx in region.index:
        current_time = df.at[idx, TIME_COLUMN]
        current_value = df.at[idx, 'Temp4']
        if prev_value is None:
            prev_time, prev_value = current_time, current_value
            continue

        if increasing:
            if prev_value < target <= current_value:
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

    # 2. Process each setpoint region.
    change_indices = find_setpoint_changes(df, SETPOINT_COLUMN)
    # Define region boundaries by including the first and last indices.
    change_indices = [0] + change_indices + [len(df)]

    results = []
    for i in range(len(change_indices) - 1):
        start_idx = change_indices[i]
        end_idx = change_indices[i + 1]

        # Duration for which the setpoint remained constant
        region_duration = df[TIME_COLUMN].iloc[end_idx - 1] - df[TIME_COLUMN].iloc[start_idx]
        current_setpoint = df[SETPOINT_COLUMN].iloc[start_idx]

        # Full-region deviations for Temp3 and Temp4 (from the setpoint)
        region_df = df.iloc[start_idx:end_idx]
        temp3_dev_region = region_df['Temp3'] - region_df[SETPOINT_COLUMN]
        temp4_dev_region = region_df['Temp4'] - region_df[SETPOINT_COLUMN]
        std_temp3_region = temp3_dev_region.std() if not temp3_dev_region.empty else None
        std_temp4_region = temp4_dev_region.std() if not temp4_dev_region.empty else None

        # 95% settling time detection for Temp3 and Temp4
        settling_time_3 = find_settling_time(df, 'Temp3', SETPOINT_COLUMN, start_idx, end_idx)
        settling_time_4 = find_settling_time(df, 'Temp4', SETPOINT_COLUMN, start_idx, end_idx)
        if settling_time_3 is not None and settling_time_4 is not None:
            # We choose the later of the two times to ensure both are within the margin.
            settling_time = max(settling_time_3, settling_time_4)
        else:
            settling_time = None

        if settling_time is not None:
            stable_df = df[(df[TIME_COLUMN] >= settling_time) & (df.index < end_idx)]
            temp3_dev_stable = stable_df['Temp3'] - stable_df[SETPOINT_COLUMN]
            temp4_dev_stable = stable_df['Temp4'] - stable_df[SETPOINT_COLUMN]
            std_temp3_stable = temp3_dev_stable.std() if not temp3_dev_stable.empty else None
            std_temp4_stable = temp4_dev_stable.std() if not temp4_dev_stable.empty else None
            time_to_settle = settling_time - df[TIME_COLUMN].iloc[start_idx]
        else:
            std_temp3_stable = None
            std_temp4_stable = None
            time_to_settle = None

        # Calculate time constant (tau) for Temp4 using the 63.2% rule
        tau_temp4 = calculate_tau_for_temp4(df, start_idx, end_idx)

        # 4d. Calculate maximum and average difference between Temp3 and Temp4 for the setpoint duration.
        diff_series = abs(region_df['Temp3'] - region_df['Temp4'])
        max_diff = diff_series.max()
        avg_diff = diff_series.mean()

        results.append({
            'Setpoint': current_setpoint,
            'StartIndex': start_idx,
            'EndIndex': end_idx,
            'SetpointDuration': region_duration,
            'SettlingTime': settling_time,
            'TimeToSettle': time_to_settle,
            'StdDev_Temp3_Region': std_temp3_region,
            'StdDev_Temp4_Region': std_temp4_region,
            'StdDev_Temp3_Stable': std_temp3_stable,
            'StdDev_Temp4_Stable': std_temp4_stable,
            'Tau_Temp4': tau_temp4,
            'Max_Diff_Temp3_Temp4': max_diff,
            'Avg_Diff_Temp3_Temp4': avg_diff
        })

    # 3. Print the results
    print("RESULTS PER SETPOINT REGION:")
    for r in results:
        print(f"Setpoint: {r['Setpoint']}")
        print(f"  StartIndex: {r['StartIndex']}, EndIndex: {r['EndIndex']}")
        print(f"  Duration of Setpoint: {r['SetpointDuration']} seconds")
        print(f"  Settling Time (95%): {r['SettlingTime']}")
        print(f"  Time To Settle (95%): {r['TimeToSettle']} seconds")
        print(f"  StdDev (Temp3, Full Region): {r['StdDev_Temp3_Region']}")
        print(f"  StdDev (Temp4, Full Region): {r['StdDev_Temp4_Region']}")
        print(f"  StdDev (Temp3, Stable): {r['StdDev_Temp3_Stable']}")
        print(f"  StdDev (Temp4, Stable): {r['StdDev_Temp4_Stable']}")
        print(f"  Time Constant Tau for Temp4: {r['Tau_Temp4']} seconds")
        print(f"  Maximum Diff (Temp3 - Temp4): {r['Max_Diff_Temp3_Temp4']}")
        print(f"  Average Diff (Temp3 - Temp4): {r['Avg_Diff_Temp3_Temp4']}")
        print("")

    # 4. Plot the temperatures and setpoint vs. time (this is now the last step)
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
