from pathlib import Path


class FileTools:
    def read_text(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")
