from plugins.base_plugin import BasePlugin


class SpotifyPlugin(BasePlugin):

    name = "Spotify Plugin"
    version = "1.0"
    description = "Controls Spotify playback"


    def __init__(self, spotify):

        self.spotify = spotify



    def can_handle(self, command):

        text = command.lower()


        return any(
            keyword in text
            for keyword in [
                "spotify",
                "music",
                "play",
                "playlist",
                "pause",
                "resume",
                "skip",
                "next",
                "previous",
                "what song",
                "what's playing"
            ]
        )



    def handle(self, command):

        text = command.lower()


        if (
            "what song" in text
            or "what's playing" in text
            or "currently playing" in text
        ):
            return self.spotify.current_song()



        if (
            "pause" in text
            or "stop music" in text
        ):
            return self.spotify.pause()



        if (
            "resume" in text
            or "continue music" in text
        ):
            return self.spotify.resume()



        if (
            "next" in text
            or "skip" in text
        ):
            return self.spotify.next_song()



        if "previous" in text:

            return self.spotify.previous_song()



        if (
            "playlist" in text
            or ("play" in text and "my" in text)
        ):

            name = (
                text
                .replace("play", "")
                .replace("my", "")
                .replace("playlist", "")
                .strip()
            )

            return self.spotify.play_playlist(
                name
            )



        query = command

        if text.startswith("play"):

            query = command[4:].strip()


        return self.spotify.play(
            query
        )