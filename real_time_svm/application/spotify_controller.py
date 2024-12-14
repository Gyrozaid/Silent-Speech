import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables from .env (You have to ask me directly for those)
load_dotenv()


class SpotifyController:
    def __init__(self):
        # Scope variable to access all the Spotify functionalities 
        scope = "ugc-image-upload, user-read-playback-state, user-modify-playback-state, user-follow-modify, user-read-private, user-follow-read, user-library-modify, user-library-read, streaming, user-read-playback-position, app-remote-control, user-read-email, user-read-currently-playing, user-read-recently-played, playlist-modify-private, playlist-read-collaborative, playlist-read-private, user-top-read, playlist-modify-public"

        # Create Spotify object with OAuth authentication 
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope=scope, 
            client_id=os.getenv("SPOTIPY_CLIENT_ID"), 
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"), 
            redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")), 
            requests_timeout=300
        )

    # Function to get the active Spotify device
    def get_active_device(self):
        devices = self.sp.devices()
        if not devices['devices']:
            print("No devices found.")
            return None
        for device in devices['devices']:
            if device['is_active']:
                print(f"Found active device: {device['name']} with ID: {device['id']}")
                return device
        print("No active devices found.")
        return None

    # Function to control Spotify playback based on command
    def control_spotify(self, command):
        device = self.get_active_device()
        if not device:
            print("No active device found. Please make sure you have an active Spotify device.")
            return
        
        device_id = device['id']

        try:
            if command == 'play':
                self.sp.start_playback(device_id=device_id)
            elif command == 'pause':
                self.sp.pause_playback(device_id=device_id)
            elif command == 'back':
                self.sp.previous_track(device_id=device_id)
            elif command == 'rewind':
                playback = self.sp.current_playback()
                current_position = playback['progress_ms']  # Current position in ms
                rewind_position = max(current_position - 15000, 0)  # Rewind 15 seconds
                self.sp.seek_track(rewind_position)

            elif command == 'skip':
                playback = self.sp.current_playback()
                current_position = playback['progress_ms']  # Current position in ms
                rewind_position = max(current_position + 15000, 0)  # skip 15 seconds
                self.sp.seek_track(rewind_position)
            else:
                print('Unknown command')
        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify exception: {e}")

if __name__ == '__main__':
    spotify_controller = SpotifyController()
    while True:
        command = input("Enter Spotify command (play, pause, back, skip): ").strip().lower()
        spotify_controller.control_spotify(command)
