import tkinter as tk
import threading
import serial
import pandas as pd
import numpy as np
import pickle
import time
from collections import deque
from sklearn.preprocessing import MinMaxScaler
from spotify_controller import SpotifyController

# Configuration
port = 'COM8'
baud_rate = 115200
threshold_magnitude = 1.1  # motion detection threshold
window_size = 3  # classification window
sample_rate = 100
target_length = 300

#load models
with open("svm_model.pkl", "rb") as file:
    svm_model = pickle.load(file)

with open("random_forest_model.pkl", "rb") as file:
    random_forest = pickle.load(file)

model = random_forest

with open("scaler.pkl", "rb") as file:
    scaler = pickle.load(file)

#vars
data_buffer = deque(maxlen=window_size * sample_rate)
motion_detected = False
motion_start_time = None
full = False
spotify = SpotifyController()
ser = None
run_detection = False


#logs message to application instead of terminal
def log_message(message):
    output_text.insert(tk.END, message + "\n")
    output_text.see(tk.END)


def motion_detection():
    global motion_detected, motion_start_time, full, run_detection, data_buffer

    try:
        ser = serial.Serial(port, baud_rate)
        ser.reset_input_buffer()
        log_message("Listening for data from ESP32...")
        log_message("Prepare for classification")

        while run_detection:
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

                    if len(data_buffer) == data_buffer.maxlen and not full:
                        full = True
                        log_message("Data buffer is full and ready to detect motion.")

                    if full:
                        acc_x, acc_y, acc_z, *_ = data_list
                        acc_magnitude = np.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

                        if acc_magnitude > threshold_magnitude:
                            if not motion_detected:
                                motion_detected = True
                                motion_start_time = time.time()
                                log_message("Motion detected! Starting classification...")

                    if motion_detected and time.time() - motion_start_time > 1.5:
                        log_message("Collecting data for classification...")
                        motion_data = np.array(data_buffer, dtype=np.float32)

                        vals = scaler.fit_transform(motion_data)

                        if vals.shape[0] < target_length:
                            padding = np.zeros((target_length - vals.shape[0], vals.shape[1]))
                            vals = np.vstack((vals, padding))
                        else:
                            vals = vals[:target_length, :]

                        X = [vals.flatten()]
                        prediction = model.predict_proba(X)[0]
                        predicted_class = model.predict(X)[0]
                        class_order = model.classes_
                        predicted_class_probability = max(prediction)
                        
                        predictions = {}
                        for i in range(len(class_order)):
                            predictions[class_order[i]] = prediction[i]

                        #hard coded probability boundaries
                        if predicted_class == 'rewind' and predicted_class_probability < .5:
                            if predictions['skip'] > .2:
                                predicted_class = 'skip'
                                predicted_class_probability = predictions['skip']
                            
                        
                        log_message(f"WORD PREDICTION: {predicted_class}, PROBABILITY: {predicted_class_probability}")
                        log_message("All probabilities:")
                        
                        for key, val in predictions.items():
                            log_message(f"{key}: {val}")

                        #spotify control
                        spotify.control_spotify(predicted_class)
                        
                        motion_detected = False
                        data_buffer.clear()

                        full = False
                        ser.reset_input_buffer()

    except Exception as e:
        log_message(f"Error: {e}")

    finally:
        if ser:
            ser.close()
            log_message("Serial connection closed.")

def start_detection():
    global run_detection
    run_detection = True
    detection_thread = threading.Thread(target=motion_detection)
    detection_thread.daemon = True
    detection_thread.start()

def stop_detection():
    global run_detection
    run_detection = False

# GUI
root = tk.Tk()
root.title("Motion Detection Control")
root.geometry("400x400")

start_button = tk.Button(root, text="Start Detection", command=start_detection, bg="green", fg="white")
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Detection", command=stop_detection, bg="red", fg="white")
stop_button.pack(pady=10)

output_text = tk.Text(root, height=15, width=50, state=tk.NORMAL)
output_text.pack(pady=10)

root.mainloop()
