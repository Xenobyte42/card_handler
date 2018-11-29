import urllib
import asyncio
import aiohttp


class CardNotFound(Exception):
    pass


class CardSeeker:

    def __init__(self, fuzzy):
        self._url = "https://api.scryfall.com/cards/named?fuzzy={}".format(fuzzy)
        self._cardjson = None

    async def get_request(self, client, url):
        async with client.get(url) as response:
            return await response.json()

    async def request(self):
        async with aiohttp.ClientSession() as client:
            self._cardjson = await self.get_request(client, self._url)

    def get_name(self):
        if self._cardjson.get('name'):
            return self._cardjson['name']
        raise CardNotFound

    def get_img_src(self):
        if self._cardjson.get('image_uris'):
            return self._cardjson['image_uris']['normal']
        raise CardNotFound
