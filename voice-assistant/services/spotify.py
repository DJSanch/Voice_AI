import subprocess


class SpotifyService:


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

            return f"Playing {query} on Spotify."

        return "I couldn't open Spotify."



    def pause(self):

        script = '''
        tell application "Spotify"
            pause
        end tell
        '''

        if self._run_script(script):
            return "Music paused."

        return "I couldn't pause Spotify."



    def resume(self):

        script = '''
        tell application "Spotify"
            play
        end tell
        '''

        if self._run_script(script):
            return "Resuming music."

        return "I couldn't resume Spotify."



    def next_song(self):

        script = '''
        tell application "Spotify"
            next track
        end tell
        '''

        if self._run_script(script):
            return "Skipping to the next song."

        return "I couldn't skip the song."



    def previous_song(self):

        script = '''
        tell application "Spotify"
            previous track
        end tell
        '''

        if self._run_script(script):
            return "Playing previous song."

        return "I couldn't go back."



    def current_song(self):

        script = '''
        tell application "Spotify"
            set currentTrack to name of current track
            set currentArtist to artist of current track
            return currentTrack & " by " & currentArtist
        end tell
        '''


        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )

            song = result.stdout.strip()

            if song:
                return f"Currently playing {song}."

            return "Nothing is playing."

        except Exception:

            return "I couldn't get the current song."