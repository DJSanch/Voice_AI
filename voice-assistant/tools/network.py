import ssl
import urllib.request


class NetworkTools:

    def build_request(self, url: str):
        return urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

    def ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

    def fetch(self, url: str):
        request = self.build_request(url)

        with urllib.request.urlopen(
            request,
            context=self.ssl_context(),
            timeout=10
        ) as response:
            return response.read().decode("utf-8")