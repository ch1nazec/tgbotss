import httpx
from typing import Optional


class HTTPClientManager:
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
    

    def get_client(self):
        if self._client is None:
            self._client = httpx.AsyncClient()
        return self._client
    
    async def close_client(self):
        if self._client:
            await self._client.aclose()
            self._client = None


http_client_manager = HTTPClientManager()