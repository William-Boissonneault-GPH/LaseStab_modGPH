import serial
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import time

# Define serial port and parameters
SERIAL_PORT = 'COM3'  # Update this with your Arduino's serial port
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

# Create a plot for real-time data
fig, ax = plt.subplots()
line_temp1, = ax.plot([], [], label='Temp1')
line_temp2, = ax.plot([], [], label='Temp2')
line_temp3, = ax.plot([], [], label='Temp3')
line_temp4, = ax.plot([], [], label='Temp4')
ax.set_xlim(0, 100)  # Time window for the plot (can be adjusted)
ax.set_ylim(0, 1023)  # Data range from analogRead() (0 to 1023 for most Arduino boards)
ax.legend()

# Function to update the plot and log data
def update_data(frame):
    global time_data, temp1_data, temp2_data, temp3_data, temp4_data
    
    # Read data from Arduino
    if arduino.in_waiting > 0:
        data = arduino.readline().decode('utf-8').strip()
        if data:
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
                    csv_writer.writerow([current_time, temp1, temp2, temp3, temp4])
                
                # Keep data within the plot window limit
                if len(time_data) > 100:
                    time_data = time_data[1:]
                    temp1_data = temp1_data[1:]
                    temp2_data = temp2_data[1:]
                    temp3_data = temp3_data[1:]
                    temp4_data = temp4_data[1:]

            except ValueError:
                pass  # Ignore invalid data

    # Update the plot
    line_temp1.set_data(time_data, temp1_data)
    line_temp2.set_data(time_data, temp2_data)
    line_temp3.set_data(time_data, temp3_data)
    line_temp4.set_data(time_data, temp4_data)

    return line_temp1, line_temp2, line_temp3, line_temp4

# Function to send a setpoint to Arduino
def send_setpoint():
    setpoint = setpoint_entry.get()
    if setpoint:
        arduino.write(f"SETPOINT:{setpoint}\n".encode())  # Send command to Arduino
    else:
        messagebox.showerror("Error", "Please enter a setpoint.")

# Function to open file dialog and select where to save the CSV file
def save_csv():
    global csv_writer, csv_file
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        # Open the file in write mode
        csv_file = open(file_path, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Time', 'Temp1', 'Temp2', 'Temp3', 'Temp4'])
        messagebox.showinfo("Info", f"CSV file will be saved to: {file_path}")

# Create input field and button to send setpoint to Arduino
setpoint_label = tk.Label(root, text="Enter Setpoint:")
setpoint_label.pack(padx=10, pady=10)
setpoint_entry = tk.Entry(root)
setpoint_entry.pack(padx=10, pady=10)
setpoint_button = tk.Button(root, text="Send Setpoint", command=send_setpoint)
setpoint_button.pack(padx=10, pady=10)

# Create a button to save the CSV file
save_button = tk.Button(root, text="Save CSV File", command=save_csv)
save_button.pack(padx=10, pady=10)

# Start real-time plot updating
start_time = time.time()  # Start time for plotting
ani = FuncAnimation(fig, update_data, interval=100, blit=True)

# Start the Tkinter GUI
tkinter_plot = plt.gcf().canvas.get_tk_widget()
tkinter_plot.pack(fill=tk.BOTH, expand=1)
root.mainloop()

# Cleanup and close the CSV file when the program exits
if csv_file:
    csv_file.close()
arduino.close()
