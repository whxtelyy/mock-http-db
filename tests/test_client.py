from unittest.mock import AsyncMock

import httpx
import pytest
import respx

from zadanie.myapp.client import FetchError, fetch_user_async

URL = "https://api.example.com/users/1"


@respx.mock
@pytest.mark.asyncio
async def test_fetch_success():
    respx.get(URL).mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Ivan"})
    )

    result = await fetch_user_async(URL)
    assert isinstance(result, dict)
    assert result["id"] == 1
    assert result["name"] == "Ivan"


@pytest.mark.asyncio
async def test_fetch_on_timeout(mocker):
    async_get = AsyncMock()
    async_get.side_effect = [
        httpx.ReadTimeout("read timeout"),
        httpx.Response(200, json={"id": 1}, request=httpx.Request("GET", URL)),
    ]

    mocker.patch("zadanie.myapp.client.httpx.AsyncClient.get", new=async_get)

    result = await fetch_user_async(URL)
    assert result == {"id": 1}
    assert async_get.call_count == 2


@respx.mock
@pytest.mark.asyncio
async def test_fetch_500():
    respx.get(URL).mock(return_value=httpx.Response(500, json={"error": "server"}))

    with pytest.raises(FetchError):
        await fetch_user_async(URL)
