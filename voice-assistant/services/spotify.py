import subprocess


class SpotifyService:

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
            set q to "{escaped_query}"
            play track "spotify:search:" & q
        end tell
        '''

        try:
            subprocess.run(
                ["osascript", "-e", script],
                check=False
            )

            return f"Playing {query} on Spotify."

        except Exception:
            return "I couldn't open Spotify."
