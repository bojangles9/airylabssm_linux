import serial
import time
import re
from datetime import datetime
import os
import csv
import subprocess

# User-controllable variables
serial_port = '/dev/ttyUSB0'  # Serial port for the device
baud_rate = 115200  # Baud rate set to 115200
data_bits = serial.EIGHTBITS
parity = serial.PARITY_NONE
stop_bits = serial.STOPBITS_ONE

# Remote server configuration
remote_host = '10.10.30.22'  # IP address of the remote host
ssh_port = '2222'  # SSH port for the remote connection
user = 'admin'  # SSH username
key_location = 'id_rsa'  # Path to the private key (local path)
remote_location = '/admin/all-sky/SSM/'  # Destination directory on the remote host

# Create output directory if it doesn't exist
output_dir = '/root/airylabssm/ssm'
os.makedirs(output_dir, exist_ok=True)

def scp_transfer(csv_file_path):
    """Transfer the CSV file to the remote host using SCP."""
    scp_command = [
        "scp",
        "-i", key_location,  # Path to your private key
        "-P", ssh_port,  # Specify the SSH port
        csv_file_path,
        f"{user}@{remote_host}:{remote_location}"  # Remote user and host
    ]
    
    # Run the SCP command and check for success
    result = subprocess.run(scp_command)
    
    if result.returncode == 0:
        print("File transferred successfully. Deleting local CSV file.")
        os.remove(csv_file_path)  # Delete the local CSV file
    else:
        print("Failed to transfer file. Retaining local CSV file.")

def start_capture():
    """Function to start capturing data from the serial port."""
    
    # Define the CSV file path with the current date and time
    start_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Format for safe file naming
    csv_file_path = os.path.join(output_dir, f"capture_{start_time}.csv")

    # Open the CSV file for appending
    with open(csv_file_path, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # Write the header to the CSV file
        csv_writer.writerow(['Time', 'Seeing Value', 'Input Value'])  # Add header

        try:
            # Configure the serial connection
            ser = serial.Serial(
                port=serial_port,
                baudrate=baud_rate,
                bytesize=data_bits,
                parity=parity,
                stopbits=stop_bits,
                timeout=1  # 1 second timeout for reading
            )

            # Regex pattern to match the desired output format
            pattern = re.compile(r"([ABC])(\d+\.\d+)\$")

            while True:
                try:
                    # Check if the serial port is still open before attempting to read
                    if ser.is_open and ser.in_waiting > 0:
                        data = ser.read(ser.in_waiting)  # Read available bytes
                        decoded_data = data.decode('utf-8')  # Decode using UTF-8

                        # Find all matches in the decoded data
                        matches = pattern.findall(decoded_data)
                        input_val = None
                        seeing_val = None

                        # Process matches to identify Input and Seeing values
                        for label, value in matches:
                            if label == 'A':  # Input value
                                input_val = value
                            elif label == 'B':  # Seeing value
                                seeing_val = value

                        # Write results to the CSV if both values are found
                        if input_val is not None and seeing_val is not None:
                            # Get current timestamp
                            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            output_row = [current_time, input_val, seeing_val]

                            # Write the data to the CSV file
                            csv_writer.writerow(output_row)
                            csv_file.flush()  # Ensure data is written to file

                except serial.SerialException:
                    print("Serial error occurred. Initiating file transfer...")
                    scp_transfer(csv_file_path)
                    break  # Break the loop to handle disconnection
                except OSError:
                    print("OS error occurred. Initiating file transfer...")
                    scp_transfer(csv_file_path)
                    break  # Break the loop to handle disconnection

        finally:
            ser.close()

# Main loop to check for the device
while True:
    if os.path.exists(serial_port):
        start_capture()  # Start capturing data if the device is found
    else:
        print(f"{serial_port} not found. Waiting for 10 seconds...")
        time.sleep(10)  # Sleep for 10 seconds before checking again
