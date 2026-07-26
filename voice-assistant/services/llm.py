import json
import urllib.request


class LLMService:
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def ask(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(
                    response.read().decode("utf-8")
                )

                return result.get("response", "").strip()

        except Exception as e:
            print("LLM Error:", e)
            return ""