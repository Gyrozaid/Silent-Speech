# Silent Speech

This repository contains code for real time prediction of words based on acceleration and angular velocity data IMU sensor connected to an ESP32S3 and attached to the jaw. Both SVM and Random Forest models are trained on CSV files containing this data for words pause, play, skip, and rewind. These predictions are then sent to the Spotify API to control music playback

Within real_time_svm:

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



# Usage

1. Flash ESP code using espressif environment
2. collect data with get_data.py
3. train svm and random forest models with machine_learning.ipynb. Make sure you have all necessary packages, recommended to use conda env
4. set up spotify .env credentials within application folder 
5. run classify.py to start the application and control spotify!


# Spotify Setup

### Step 1: Create a Virtual Environment
```bash
python3 -m venv 528_project_venv
```

### Step 2: Activate the Virtual Environment
- **On macOS/Linux:**
  ```bash
  source 528_project_venv/bin/activate
  ```
- **On Windows:**
  ```bash
  528_project_venv\Scripts\activate
  ```

## Installing Dependencies
Once the virtual environment is activated, install the following Python packages:

```bash
pip install python-dotenv
pip install spotipy
```

## Setting Up Spotify API
To control Spotify, you need to set up a Spotify Developer account and create an app.

### Step 1: Create a Spotify Developer Account
1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) and log in with your Spotify account.
2. Click on "Create an App" and fill in the required details.

### Step 2: Get Client ID and Client Secret
After creating the app, you'll find the **Client ID** and **Client Secret** on the app dashboard. 

### Step 3: Store Credentials
Create a `.env` file in the root directory of your project and add the following lines:

```plaintext
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=your_redirect_uri
```

# Spotify  
## Python Environment Setup

### Creating an environment with venv
```
python3 -m venv 528_project
```

# Activate the virtual environment
# On Windows
```
528_project\Scripts\activate
```
# On macOS/Linux
```
source 528_project/bin/activate
```

# Install required packages
```
pip install python-dotenv
pip install spotipy
```

# Running the Project

```
python Silent-Speech/Spotify/main.py
```

You will be prompted to enter commands such as **play**, **pause**, **resume**, **back**, and **skip**.

