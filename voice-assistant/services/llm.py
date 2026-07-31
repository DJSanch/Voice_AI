import json
import urllib.request
import base64


class LLMService:

    def __init__(
        self,
        model: str = "llama3.2:3b"
    ):

        self.model = model
        self.url = "http://localhost:11434/api/generate"



    def ask(
        self,
        prompt: str
    ) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }


        return self._send(payload)



    def ask_image(
        self,
        prompt: str,
        image_path: str
    ) -> str:


        with open(
            image_path,
            "rb"
        ) as image:

            encoded = base64.b64encode(
                image.read()
            ).decode(
                "utf-8"
            )


        payload = {

            "model": "moondream",

            "prompt": prompt,

            "images": [
                encoded
            ],

            "stream": False
        }


        return self._send(payload)



    def _send(
        self,
        payload
    ):

        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload).encode(
                "utf-8"
            ),
            headers={
                "Content-Type": "application/json"
            },
        )


        try:

            with urllib.request.urlopen(
                request,
                timeout=200
            ) as response:

                result = json.loads(
                    response.read().decode(
                        "utf-8"
                    )
                )

                return result.get(
                    "response",
                    ""
                ).strip()


        except Exception as e:

            print(
                "LLM Error:",
                e
            )

            return ""