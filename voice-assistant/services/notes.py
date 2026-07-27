import json
import os
from datetime import datetime


NOTES_FILE = "data/notes.json"


class NotesService:

    def __init__(self):
        self._create_storage()


    def _create_storage(self):
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "w") as file:
                json.dump([], file)


    def _load_notes(self):
        try:
            with open(NOTES_FILE, "r") as file:
                return json.load(file)

        except (json.JSONDecodeError, FileNotFoundError):
            return []


    def _save_notes(self, notes):
        with open(NOTES_FILE, "w") as file:
            json.dump(
                notes,
                file,
                indent=4
            )


    def add_note(self, text):

        notes = self._load_notes()

        note = {
            "text": text,
            "created": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        }

        notes.append(note)

        self._save_notes(notes)

        return f"Note saved: {text}"


    def get_notes(self):

        notes = self._load_notes()

        if not notes:
            return "You don't have any notes."

        response = "Here are your notes:\n"

        for index, note in enumerate(notes, start=1):
            response += (
                f"{index}. {note['text']} "
                f"({note['created']})\n"
            )

        return response


    def clear_notes(self):

        self._save_notes([])

        return "All notes have been cleared."