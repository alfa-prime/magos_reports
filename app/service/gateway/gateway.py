import httpx
from app.core import get_settings
from app.core.decorators import log_and_catch

settings = get_settings()


class GatewayService:
    GATEWAY_ENDPOINT = settings.GATEWAY_REQUEST_ENDPOINT

    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    @log_and_catch()
    async def make_request(self, method: str, **kwargs) -> dict:
        if not hasattr(self._client, method.lower()):
            raise ValueError(f"Неподдерживаемый HTTP метод: {method}")

        http_method_func = getattr(self._client, method.lower())
        response = await http_method_func(url=self.GATEWAY_ENDPOINT, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    @log_and_catch()
    async def download(self, url: str, method: str = "POST", **kwargs) -> bytes:
        """
        Метод для скачивания файлов.
        """
        response = await self._client.request(method=method, url=url, **kwargs)

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Error {response.status_code}: {response.text[:200]}",
                request=response.request,
                response=response
            )

        return response.content
