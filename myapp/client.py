from typing import Any, Optional

import httpx


class FetchError(Exception):
    pass


async def fetch_user_async(
    url: str, retries: int = 2, timeout: float = 2.0, fallback: Optional[Any] = None
) -> Any:
    attempt = 0
    while attempt < retries:
        attempt += 1
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()

        except httpx.ReadTimeout:
            if attempt >= retries:
                break
            continue

        except httpx.HTTPStatusError as exc:
            if fallback is not None:
                return fallback
            raise FetchError(f"HTTP error {exc}") from exc

        except Exception as exc:
            if fallback is not None:
                return fallback
            raise FetchError(f"Other error {exc}") from exc

    if fallback is not None:
        return fallback
    raise FetchError(f":(")
