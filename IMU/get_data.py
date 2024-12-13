import serial
import pandas as pd
import time

# Configuration
port = 'COM8'
baud_rate = 115200  
ser = serial.Serial(port, baud_rate)


# Parameters for recording
words = ["play", 'pause', 'skip', 'rewind']
num_repeats = 20
record_duration = 4 
delay_between_words = 2  

try:
    print("Listening for data from ESP32...")

    for word in words:
        for repeat in range(num_repeats):
            df_list = []
            print(f"Recording word: {word} (Repeat {repeat + 1}/{num_repeats})")
            
            for i in reversed(range(1, 4)):
                print(i)
                time.sleep(1)

            print('TRAINING START')
            
            start_time = time.time()
            while time.time() - start_time < record_duration:
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
                        df_list.append(data_list)
                        print(data_list)
                            
            df = pd.DataFrame(df_list, columns=['acc_x', 'acc_y', 'acc_z', 'gyro_x', 'gyro_y', 'gyro_z', 'temp'])
            df.to_csv(f"C:\\Users\\ryanz\\Documents\\CS528\\project\\IMU\\data\\sensor_data_{word}_{repeat}.csv", index=False)


            print(f"Finished recording {word}. Writing CSV and pausing for {delay_between_words} seconds...")
            
            time.sleep(delay_between_words)

except KeyboardInterrupt:
    print("Data capture interrupted.")

finally:    
    print("Stopping data capture...")
    ser.close()
    print("Serial connection closed.")
