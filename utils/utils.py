"""
Utilities functions for the project

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

import datetime
from typing import Union

import aiohttp


class Utils:
    """
    Utilities class with various functions.
    """

    ratelimit = {}

    @classmethod
    async def api_request(cls, url: str, headers: dict = None) -> Union[dict, int]:
        """
        Make an API request.
        This only works with JSON APIs with GET requests.

        :param url: The URL to make the request to.
        :type url: str
        :param headers: The headers to send with the request.
        :type headers: dict

        :return: The response from the API or the status code if the request was ratelimited.
        :rtype: Union[dict, int]
        """
        if url.startswith(
            "https://api.trace.moe/search?url="
        ) and datetime.datetime.utcnow().timestamp() < cls.ratelimit.get("trace.moe", 0):
            return 429
        async with aiohttp.ClientSession() as s, s.get(url, headers=headers) as r:
            if r.status == 402:
                return 402
            if r.status == 429:
                if url.startswith("https://api.trace.moe/search?url="):
                    cls.ratelimit["trace.moe"] = r.headers["x-ratelimit-reset"]
                return 429
            return await r.json()
