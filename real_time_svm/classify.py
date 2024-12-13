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
target_length = 300



with open("svm_model.pkl", "rb") as file:
    svm_model = pickle.load(file)
    
with open("scaler.pkl", "rb") as file:
    scaler = pickle.load(file)

data_buffer = deque(maxlen=window_size * sample_rate)
motion_detected = False
motion_start_time = None
full = False


try:
    print("Listening for data from ESP32...")
    run = True
    
    print(f"prepare for classification")
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

                data_buffer.append(data_list[:6])
                
                if (len(data_buffer) == data_buffer.maxlen) and not full:
                    full = True
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
                            print("Motion detected! Starting classification...")


                
                #record 1.5 more seconds after motion, keep 1.5 seconds before motion
                if motion_detected and time.time() - motion_start_time > 1.5:
                    print("Collecting data for classification...")
                    motion_data = np.array(data_buffer, dtype=np.float32)
                    print(motion_data.shape[0])
                    
                    
                    vals = scaler.fit_transform(motion_data)
                    
                    #pad arrays with zeros
                    if vals.shape[0] < target_length:
                        padding = np.zeros((target_length - vals.shape[0], vals.shape[1]))
                        vals = np.vstack((vals, padding))
                    else:
                        vals = vals[:target_length, :]
                    
                    X = [vals.flatten()]
                    
                    prediction = svm_model.predict_proba(X)[0]                  
                    predicted_class = svm_model.predict(X)[0]
                    
                    class_order = svm_model.classes_
                    predicted_class_probability = max(prediction)
                    
                    
                    print(f"WORD PREDICTION: {predicted_class}, PROBABILITY: {predicted_class_probability}\n")
                    print(f"All probabilities:")
                    for i in range(len(class_order)):
                        print(f"{class_order[i]}: {prediction[i]}")

                    

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
                    ser.reset_input_buffer()
                    


except KeyboardInterrupt:
    print("Real-time gesture classification interrupted.")

finally:
    print("Stopping classification...")
    ser.close()
    print("Serial connection closed.")
