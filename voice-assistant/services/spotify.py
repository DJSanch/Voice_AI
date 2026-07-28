import os
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()


class SpotifyService:

    def __init__(self):

        self.playing = False

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope=[
                    "user-read-playback-state",
                    "user-modify-playback-state",
                    "playlist-read-private",
                    "playlist-read-collaborative",
                    "user-library-read",
                    "user-read-currently-playing",
                ]
            )
        )


    def _run_script(self, script: str):

        try:
            subprocess.run(
                ["osascript", "-e", script],
                check=False
            )

            return True

        except Exception as e:
            print("Spotify Error:", e)
            return False



    def play_playlist(self, playlist_name: str) -> str:

        try:

            playlists = self.sp.current_user_playlists(
                limit=50
            )

            target = playlist_name.lower()

            for playlist in playlists["items"]:

                if target in playlist["name"].lower():

                    self.sp.start_playback(
                        context_uri=playlist["uri"]
                    )
                    self.playing = True

                    return (
                        f"Playing your playlist "
                        f"{playlist['name']}."
                    )


            return (
                f"I couldn't find your playlist "
                f"{playlist_name}."
            )


        except Exception as e:

            print(
                "Spotify API Error:",
                e
            )

            return (
                "I couldn't access your Spotify playlists."
            )



    def play(self, query: str) -> str:

        if not query:
            query = "music"


        escaped_query = (
            query
            .replace("\\", "\\\\")
            .replace('"', '\\"')
        )


        script = f'''
        tell application "Spotify"
            activate
            play track "spotify:search:{escaped_query}"
        end tell
        '''


        if self._run_script(script):

            self.playing = True

            return f"Playing {query} on Spotify."

        return "I couldn't open Spotify."



    def pause(self):

        script = '''
        tell application "Spotify"
            pause
        end tell
        '''

        self._run_script(script)

        self.playing = False

        return "Music paused."



    def resume(self):

        script = '''
        tell application "Spotify"
            play
        end tell
        '''

        self._run_script(script)

        self.playing = True

        return "Resuming music."



    def next_song(self):

        script = '''
        tell application "Spotify"
            next track
        end tell
        '''

        self._run_script(script)

        return "Skipping to the next song."