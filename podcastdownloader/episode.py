#!/usr/bin/env python3
# coding=utf-8

import logging
import mimetypes
import re
import urllib.parse
from pathlib import Path
from typing import Optional

import aiohttp
from multidict import CIMultiDictProxy

from podcastdownloader.exceptions import EpisodeException

logger = logging.getLogger(__name__)


class Episode:
    def __init__(self, title_name: str, episode_url: str, podcast_name: str):
        self.title = title_name
        self.url = episode_url
        self.podcast_name = podcast_name
        self.file_path: Optional[Path] = None

    @staticmethod
    def parse_dict(feed_dict: dict, podcast_name: str) -> 'Episode':
        episode_url = Episode._find_url(feed_dict)
        result = Episode(
            feed_dict['feed']['title'],
            episode_url,
            podcast_name,
        )
        return result

    def _calculate_path(self, destination: Path, extension: str):
        file_name = self.title + extension
        self.file_path = Path(destination, self.podcast_name, file_name)

    @staticmethod
    def _find_url(feed_dict: dict) -> str:
        mime_type_regex = re.compile(r'^audio.*')
        valid_urls = list(filter(lambda u: re.match(mime_type_regex, u['type']), feed_dict['links']))
        if valid_urls:
            return valid_urls[0].get('href')
        else:
            raise EpisodeException('Could not find a valid link')

    @staticmethod
    def _get_file_extension(url: str, headers: CIMultiDictProxy) -> str:
        url = urllib.parse.urlsplit(url).path
        mime_type = mimetypes.guess_type(url)[0]
        if not mime_type:
            mime_type = headers.get('Content-Type')
        if not mime_type:
            raise EpisodeException(f'Could not determine MIME type for URL {url}')
        result = mimetypes.guess_extension(mime_type)
        if result:
            return result
        else:
            raise EpisodeException(f'Could not determine file extension for download {url}')

    async def download(self, destination: Path, session: aiohttp.ClientSession):
        async with session.get(self.url) as response:
            file_extension = self._get_file_extension(self.url, response.headers)
            self._calculate_path(destination, file_extension)
            if not self.file_path.exists():
                data = await response.content.read()
                with open(self.file_path, 'wb') as file:
                    file.write(data)
                logger.info(f'Downloaded {self.title} in podcast {self.podcast_name}')
            else:
                logger.debug(f'File already exists at {self.file_path}')