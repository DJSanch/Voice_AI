from plugins.base_plugin import BasePlugin


class NotesPlugin(BasePlugin):

    name = "Notes Plugin"
    version = "1.0"
    description = "Manages Astra notes"


    def __init__(self, notes):

        self.notes = notes



    def can_handle(self, command):

        text = command.lower()

        return any(
            phrase in text
            for phrase in [
                "take a note",
                "remember",
                "show my notes",
                "read my notes",
                "clear my notes"
            ]
        )



    def handle(self, command):

        text = command.lower()


        if (
            "show my notes" in text
            or "read my notes" in text
        ):

            return self.notes.get_notes()



        if "clear my notes" in text:

            return self.notes.clear_notes()



        if "take a note" in text:

            note = (
                command.lower()
                .split(
                    "take a note",
                    1
                )[1]
                .strip()
            )

            return self.notes.add_note(note)



        if "remember" in text:

            note = (
                command.lower()
                .split(
                    "remember",
                    1
                )[1]
                .strip()
            )

            return self.notes.add_note(note)


        return "I could not process that note."