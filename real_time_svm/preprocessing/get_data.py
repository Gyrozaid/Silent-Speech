import serial
import pandas as pd
import numpy as np
import pickle
import time
from collections import deque
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns


# Configuration
port = 'COM8'
baud_rate = 115200
ser = serial.Serial(port, baud_rate)
threshold_magnitude = 1.1  #motion detection threshold
window_size = 3  #classification window
sample_rate = 100
num_saves = 0
gestures = ["play", "pause", "skip", "rewind"]
num_repeats = 41


data_buffer = deque(maxlen=window_size * sample_rate)
motion_detected = False
motion_start_time = None
full = False

try:
    print("Listening for data from ESP32...")

    for gesture in gestures:
        for repeat in range(21, num_repeats):
            run = True
            print(f"prepare for data collection: {gesture}: {repeat}")
            ser.reset_input_buffer()

            while run:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    data_str = line.split(':')[-1]
                    data_list = []
                    for x in data_str.split(","):
                        try:
                            data_list.append(float(x))
                        except ValueError:
                            pass
                    if len(data_list) == 7:
                        if len(data_buffer) == 0:
                            buffer_start_time = time.time()  # Start timing

                        data_buffer.append(data_list[:6])
                        if (len(data_buffer) == data_buffer.maxlen) and not full:
                            full = True
                            buffer_fill_time = time.time() - buffer_start_time  # Calculate elapsed time
                            print(buffer_fill_time)
                            print("Data buffer is full and ready to detect motion.")

                        if full:
                            #calculate magnitude
                            acc_x, acc_y, acc_z, *_ = data_list
                            acc_magnitude = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

                            #threshold magnitude
                            if acc_magnitude > threshold_magnitude:
                                if not motion_detected:
                                    motion_detected = True
                                    motion_start_time = time.time()
                                    print("Motion detected! Starting data retrieval...")


                            
                            #record 1.5 more seconds after motion, keep 1.5 seconds before motion
                            if motion_detected and time.time() - motion_start_time > 1.5:
                                print("Collecting data for classification...")
                                motion_data = np.array(data_buffer, dtype=np.float32)
                                df = pd.DataFrame(motion_data, columns=['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z'])
                                df.to_csv(f"C:\\Users\\ryanz\\Documents\\CS528\\project\\real_time_svm\\data\\sensor_data_{gesture}_{repeat}.csv", index=False)

                                #reset motion detection
                                motion_detected = False
                                data_buffer.clear()
                                print(f"data buffer length: {len(data_buffer)}")
                                
                                #reset position 
                                print("Reset your position in ...")
                                for i in range(3, 0, -1):
                                    print(f"{i}...")
                                    time.sleep(1)
                                    
                                full = False
                                run = False






                        
                        
                    

except KeyboardInterrupt:
    print("Real-time data retrieval interrupted.")

finally:
    print("Stopping data retrieval...")
    ser.close()
    print("Serial connection closed.")
