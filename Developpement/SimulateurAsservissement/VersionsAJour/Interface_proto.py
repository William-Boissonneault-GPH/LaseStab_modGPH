import serial
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time
import numpy as np

csv_writer = None
csv_file = None

# Define serial port and parameters
SERIAL_PORT = 'COM14'  # Update this with your Arduino's serial port
BAUD_RATE = 9600
arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# Create a Tkinter window
root = tk.Tk()
root.title("Arduino Data Logger")

# Create variables to hold the data
time_data = []
temp1_data = []
temp2_data = []
temp3_data = []
temp4_data = []

# Create variables to hold the data
time_data = []
temp1_data = []
temp2_data = []
temp3_data = []
temp4_data = []

lastError = 999
lastCommand = 999
lastSetpoint = 999

# Create a plot for real-time data
fig, ax = plt.subplots()
scatter_temp1 = ax.scatter([], [], label='T1_mesure')
scatter_temp2 = ax.scatter([], [], label='T2_mesure')
scatter_temp3 = ax.scatter([], [], label='T3_estimr')
scatter_temp4 = ax.scatter([], [], label='T3_mesure')
ax.set_xlim(0, 100)  # Time window for the plot (can be adjusted)
ax.set_ylim(12,38)  # Data range from analogRead() (0 to 1023 for most Arduino boards)
ax.legend()

# Function to update the plot and log data
def update_data(frame):
    global time_data, temp1_data, temp2_data, temp3_data, temp4_data
    global lastError, lastCommand, lastSetpoint
    # Read data from Arduino
    
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        print(data)
        if data:
            if data[0]=="e":
                try:
                    parts = data.split(', ')
                    
                    lastError = float(parts[0].split(':')[1])
                    lastCommand = int(parts[1].split(':')[1])
                    lastSetpoint = float(parts[2].split(':')[1])
                except ValueError:
                    pass
            else:
                try:
                    time_str, temp1, temp2, temp3, temp4 = data.split(',')
                    current_time = time.time() - start_time  # Calculate elapsed time
                    time_data.append(current_time)
                    temp1_data.append(float(temp1))
                    temp2_data.append(float(temp2))
                    temp3_data.append(float(temp3))
                    temp4_data.append(float(temp4))

                    # Log data to CSV
                    if csv_writer:
                        csv_writer.writerow([current_time, temp1, temp2, temp3, temp4, lastError, lastCommand, lastSetpoint])
                    
                    # Keep data within the plot window limit
                    if len(time_data) > 100:
                        time_data = time_data[1:]
                        temp1_data = temp1_data[1:]
                        temp2_data = temp2_data[1:]
                        temp3_data = temp3_data[1:]
                        temp4_data = temp4_data[1:]

                except ValueError:
                    raise  # Ignore invalid data

    # Ensure that offsets is a 2D array: we create a list of (time, temp) pairs
    scatter_temp1.set_offsets(np.column_stack((time_data, temp1_data)))
    scatter_temp2.set_offsets(np.column_stack((time_data, temp2_data)))
    scatter_temp3.set_offsets(np.column_stack((time_data, temp3_data)))
    scatter_temp4.set_offsets(np.column_stack((time_data, temp4_data)))

    if frame%10 == 0 and len(time_data) > 0:
        ax.set_xlim(max(time_data)-90, max(time_data)+10)  # Time axis dynamically adjusts
        #ax.set_ylim(min(min(temp1_data), min(temp2_data), min(temp3_data), min(temp4_data)),
        #        max(max(temp1_data), max(temp2_data), max(temp3_data), max(temp4_data)))
    
    return scatter_temp1, scatter_temp2, scatter_temp3, scatter_temp4

# Function to send a setpoint to Arduino
def send_setpoint():
    setpoint = setpoint_entry.get()
    if setpoint:
        arduino.write(f"SETPOINT:{setpoint}\n".encode())  # Send command to Arduino
    else:
        messagebox.showerror("Error", "Please enter a setpoint.")

def send_command():
    command = command_entry.get()
    if command:
        arduino.write(f"ASSERVT3:{command}\n".encode())  # Send custom command to Arduino
    else:
        messagebox.showerror("Error", "Please enter a command.")

# Function to open file dialog and select where to save the CSV file
def save_csv():
    global csv_writer, csv_file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        # Open the file in write mode
        csv_file = open(file_path, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Temp1', 'Temp2', 'Temp3', 'Temp4', 'Erreur', 'Commande PWM', 'Setpoint'])
        messagebox.showinfo("Info", f"CSV file will be saved to: {file_path}")

# Create input field and button to send setpoint to Arduino
setpoint_label = tk.Label(root, text="Enter Setpoint:")
setpoint_label.pack(padx=10, pady=10)
setpoint_entry = tk.Entry(root)
setpoint_entry.pack(padx=10, pady=10)
setpoint_button = tk.Button(root, text="Send Setpoint", command=send_setpoint)
setpoint_button.pack(padx=10, pady=10)

# Create input field and button to send custom command to Arduino
command_label = tk.Label(root, text="0 pour asservir T3_estimé, 1 pour T3:")
command_label.pack(padx=10, pady=10)
command_entry = tk.Entry(root)
command_entry.pack(padx=10, pady=10)
command_button = tk.Button(root, text="Choisir Asserv", command=send_command)
command_button.pack(padx=10, pady=10)

# Create a button to save the CSV file
save_button = tk.Button(root, text="Start CSV logging File", command=save_csv)
save_button.pack(padx=10, pady=10)

# Start real-time plot updating
start_time = time.time()  # Start time for plotting
ani = FuncAnimation(fig, update_data, interval=100)

# Start the Tkinter GUI
tkinter_plot = plt.gcf().canvas.get_tk_widget()
tkinter_plot.pack(fill=tk.BOTH, expand=1)
plt.show()
root.mainloop()

# Cleanup and close the CSV file when the program exits
if csv_file:
    csv_file.close()
arduino.close()
