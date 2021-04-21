#!/usr/bin/env python3

import asyncio
import itertools
import logging
import sys
from asyncio.queues import Queue
from pathlib import Path

import aiohttp
import click

import podcastdownloader.utility_functions as util
from podcastdownloader.exceptions import EpisodeException, PodcastException
from podcastdownloader.podcast import Podcast

logger = logging.getLogger()


def _setup_logging(verbosity: int):
    logger.setLevel(1)
    stream = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s - %(name)s - %(levelname)s] - %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    if verbosity >= 1:
        stream.setLevel(logging.DEBUG)
    else:
        stream.setLevel(logging.INFO)
    logging.getLogger('asyncio').setLevel(logging.CRITICAL)
    logging.getLogger('chardet').setLevel(logging.CRITICAL)


_common_options = [
    click.argument('destination', type=str),
    click.option('-v', '--verbose', type=int, default=0, count=True),
    click.option('-f', '--feed', type=str, multiple=True, default=[]),
    click.option('-F', '--file', type=str, multiple=True, default=[]),
    click.option('--opml', type=str, multiple=True, default=[]),
]


async def fill_individual_feed(in_queue: Queue, out_queue: Queue, session: aiohttp.ClientSession):
    while not in_queue.empty():
        podcast = await in_queue.get()
        if podcast is None:
            break
        logger.debug(f'Beginning retrieval for {podcast.url}')
        try:
            await podcast.download_feed(session)
        except PodcastException as e:
            logger.error(e)
        except Exception:
            logger.critical(f'Error with {podcast.url}')
            raise
        else:
            await out_queue.put(podcast)
            logger.info(f'Retrieved RSS for {podcast.name}')
        in_queue.task_done()


async def download_individual_episode(in_queue: Queue, destination: Path, session: aiohttp.ClientSession):
    while not in_queue.empty():
        episode = await in_queue.get()
        if episode is None:
            break
        logger.debug(f'Attempting download of episode {episode.title} in {episode.podcast_name}')
        try:
            await episode.download(destination, session)
        except EpisodeException as e:
            logger.error(e)
        in_queue.task_done()


def add_common_options(func):
    for option in _common_options:
        func = option(func)
    return func


@click.group()
def cli():
    pass


@cli.command('download')
@add_common_options
@click.option('-t', '--threads', type=int, default=10)
def cli_download(destination: str, verbose: int, feed: tuple[str], file: tuple[str], opml: tuple[str], threads: int):
    _setup_logging(verbose)
    destination = Path(destination).expanduser().resolve()
    if not destination.exists():
        logger.warning(f'Specified destination {destination} does not exist, creating it now')
        destination.mkdir(parents=True)

    all_feeds = set(itertools.chain(feed, util.load_feeds_from_text_file(file), util.load_feeds_from_opml(opml)))
    logger.info(f'{len(all_feeds)} feeds found')
    if all_feeds:
        asyncio.run(download_episodes(all_feeds, destination, threads))
    else:
        logger.error('No feeds have been provided')
    logger.info('Program Complete')


async def download_episodes(all_feeds: set[str], destination: Path, threads: int):
    unfilled_podcasts = Queue()
    filled_podcasts = Queue()
    episodes = Queue()
    [await unfilled_podcasts.put(Podcast(url)) for url in all_feeds]
    async with aiohttp.ClientSession() as session:
        feed_fillers = [asyncio.create_task(
            fill_individual_feed(unfilled_podcasts, filled_podcasts, session)
        ) for _ in range(1, threads)]
        await asyncio.gather(*feed_fillers)
        await unfilled_podcasts.join()
        logger.info('All feeds filled')
        podcasts = []
        while not filled_podcasts.empty():
            podcasts.append(filled_podcasts.get_nowait())
        [await episodes.put(ep) for feed in podcasts for ep in feed.episodes]
        episode_downloaders = [asyncio.create_task(
            download_individual_episode(episodes, destination, session)
        ) for _ in range(1, threads)]
        await asyncio.gather(*episode_downloaders)
        await episodes.join()


if __name__ == '__main__':
    cli()
