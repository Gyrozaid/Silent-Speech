# ML classification of jaw motion into words!

This repository contains code for real time prediction of words based on acceleration and angular velocity data IMU sensor connected to an ESP32S3 and attached to the jaw. Both SVM and Random Forest models are trained on CSV files containing this data for words pause, play, skip, and rewind. These predictions are then sent to the Spotify API to control music playback



- main:
    - main.c: build and flash to ESP32S3 to output x, y, z acceleration and gyroscope data as well as temperature to monitor

- preprocessing:
    - get_data.py: listens to output from ESP32S3 and outputs to csv files. 
    - machine_learning.ipynb: code to train ML models

- data:
    - all CSV files used in analysis

- old_data:
    - unused CSV files

- application:
    - .pkl files for the preprocessing scaler and ML models
    - classify.py: real time classification code
    - spotify_controller.py: Spotify API implementation. Imported into classify.py