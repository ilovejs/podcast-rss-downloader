# podcast-downloader

## Mission

Backup your favorite podcast channel before they delete it.

## Brief

Promise to work on 21st Jan 2023 for Podbean.com at least.

Original code can pass rss feed, i modifed to only export url in the feed.

So, aria2c can be used to traffic control. aka show progress, multithread.

First,

e.g. https://traderchats.podbean.com/ has rss button on the left, just below profile picture.
click that leads to rss feed. https://feed.podbean.com/traderchats/feed.xml

another example is https://anchor.fm/s/3cbbb3b8/podcast/rss

Second, plz check it's beautiful output :)

/home/mic/venv/podcast-downloader/bin/python /home/mic/SourceCode/BE/podcast-downloader/podcastdownloader/__main__.py download --feed https://feed.podbean.com/traderchats/feed.xml out 
[2023-01-21 02:31:17,594 - root - INFO] - Retrieved RSS for Trader Chats
[2023-01-21 02:31:17,594 - root - INFO] - All feeds filled
[2023-01-21 02:31:17,595 - root - INFO] - 16 episodes to download
https://mcdn.podbean.com/mf/web/z6mi2m/Episode_2_-_Wisdom_of_Charts8jsng.mp3
https://mcdn.podbean.com/mf/web/sku25b/Q4_Roundtable_The_Year_of_Pain_-_Melt_Up_or_Melt_Down_to_End_2022_bo0k9.m4a
https://mcdn.podbean.com/mf/web/2e6v49/Ep_6_The_Importance_of_Positioning_awkdh.mp3
https://mcdn.podbean.com/mf/web/drxhm2/BOND_MARKETS-_SIGNAL_OR_NOISE_6ro95.mp3
https://mcdn.podbean.com/mf/web/w9svcv/Ep_3_Can_Trading_Skills_Save_Lives_8g9c8.mp3
https://mcdn.podbean.com/mf/web/ryt3tx/Trader_Chat_s_Podcast9fef1.mp3
https://mcdn.podbean.com/mf/web/uakb6r/Ep_7_Traders_That_Teach78g06.mp3
https://mcdn.podbean.com/mf/web/jd9w7p/Ep_4_Simon_Harrisbdcun.mp3
https://mcdn.podbean.com/mf/web/g3jjt6/Ep_8_Quant_driven_asset_allocation6cn2r.mp3
https://mcdn.podbean.com/mf/web/5t73qj/Q3_Audio6tzxz.mp3
https://mcdn.podbean.com/mf/web/na4i8m/Ep_5_Tony_Greer9je63.mp3
https://mcdn.podbean.com/mf/web/3vt8h9/Q2_2070cg8.mp3
https://mcdn.podbean.com/mf/web/yei3iv/Ep_4_Why_Leave_Banking_205zm96.mp3
https://mcdn.podbean.com/mf/web/ra6ziu/Ep_5_From_Banking_to_De-Fi8c649.mp3
https://mcdn.podbean.com/mf/web/esad3x/Epsiode_1_-_Bursting_the_AMC_bubble6iwfz.mp3
https://mcdn.podbean.com/mf/web/mxzqtz/Tracking_Bitcoin_Cyclesawey0.mp3

Third,

copy into trade.txt for all generated urls above

aria2c -x 10 -i trade.txt

## Quick start (whole process for run python in zsh)

Basically, we redo the process again, so you can download / backup ur favorite podcast tonight.

mkdir out

pycharm run __main__.py with param:

download --feed https://feed.podbean.com/traderchats/feed.xml out

touch trade.txt with url links from above stdin output

aria2c -x 10 -i trade.txt


## Usage

`python3 -m podcastdownloader download   --help`

Usage: python -m podcastdownloader download [OPTIONS] DESTINATION

Options:
  --opml TEXT
  -F, --file TEXT
  -f, --feed TEXT
  -v, --verbose
  -l, --limit INTEGER
  -t, --threads INTEGER
  -w, --write-playlist [m3u]
  --help                      Show this message and exit.


## Intro

This is a simple tool for downloading all the available episodes in an RSS feed to disk, where they can be listened to offline.

Firstly, Python 3 must be installed, then the requirements must be installed. These are documented in `requirements.txt` and can be installed via the command `python3 -m pip install -r requirements.txt`.

## out of date cli args

Following are the arguments that can be supplied to the program:

- `destination` is the directory that the folder structure will be created in and the podcasts downloaded to
- `-f, --feed` is the URL for the RSS feed of the podcast
- `-o, --opml` is the location of an OPML file with podcast data
- `--file` is the location of a simple text file with an RSS feed URL on each line
- `-l, --limit` is the maximum number of episodes to try and download from the feed; if left blank, it is all episodes, but a small number is fastest for updating a feed
- `-m, --max-downloads` will limit the number of episodes to be downloaded to the specified integer
- `-w, --write-list` is the option to write an ordered list of the episodes in the podcast in several different formats, as specified:
  - `none`
  - `text`
  - `audacious`
  - `m3u`
- `-t, --threads` is the number of threads to run concurrently; defaults to 10
- `--max-attempts` will specify the number of reattempts for a failed or refused connection; see below for more details

The following arguments alter the functioning of the program in a major way e.g. they do not download:

- `--skip-download` will do everything but download the files; useful for updating episode playlists without a lengthy download
- `--verify` will scan existing files for ones with a file-size outside a 2% and list them in `results.txt`
- `--update-tags` will download episode information and write tags to all episodes already downloaded

The following arguments alter the verbosity and logging behaviour:

- `-s, --suppress-progress` will disable all progress bars
- `-v, --verbose` will increase the verbosity of the information output to the console
- `--log` will log all messages to a debug level (the equivalent of `-v`) to the specified file, appending if it already exists

The `--feed`, `--file`, and `--opml` flags can all be specified multiple times to aggregate feeds from multiple locations.

Of these, only the destination is required, though one or more feeds or one or more OPML files must be provided or the program will just complete instantly.

### Maximum Reattempts

In some cases, particularly when downloading a single or a few specific podcasts with a lot of episodes at once, the remote server will receive a number of simultaneous or consecutive requests. As this may appear to be atypical behaviour, this server may refuse or close incoming connections as a rate-limiting measure. This is normal in scraping servers that do not want to be scraped.

There are several countermeasures in the downloader for this behaviour, such as randomising the download list to avoid repeated calls to the same server in a short amount of time, but this may not work if there is only one or a few podcast feeds to download. As such, the method of last resort is a sleep function to wait until the server allows the download to continue. This is done with increasing increments of 30 seconds, with the maximum number or reattempts specified by the `--max-attempts` argument. For example, if left at the default of 10, the program will sleep for 30 seconds if the connection is refused. Then, if it was refused again, it will sleep for 60 before reattempting the download. It will do this until the 10th attempt, where it will sleep for 300 seconds, or five minutes. If the connection is refused after this, then an error will occur and the download thread will move on to the next podcast episode.

The maximum number of reattempts may need to be changed in several cases. If you wish to download the episode regardless of anything else, then you may want to increase the argument. This may result in longer wait times for the downloads to complete. However, a low argument will make the program skip downloads if they time out repeatedly, missing content but completing faster.

### Warnings

The `--write-list` option should not be used with the `--limit` option. The limit option will be applied to the episode list in whatever format chosen, and this will overwrite any past episode list files. For example, if a `--limit` of 5 is chosen with `-w audacious`, then the exported Audacious playlist will only be 5 items long. Thus the `-w` option should only be used when there is not a limit.

## Tags

The downloader has basic tag writing support. It will write ID3 tags to MP3 files and iTunes-compatible tags to m4a and MP4 files. The information written is as follows:

- The episode title
- The podcast title
- The publishing date and time of the episode
- The description accompanying the episode
- The episode number (if available)

## Example Command

Following is an example command to download a single feed to a podcasts folder.

`python3 -m podcastdownloader media/podcasts --f 'http://linustechtips.libsyn.com/wanshow' -o podcasts.opml`

python3 -m podcastdownloader download --feed 'http://linustechtips.libsyn.com/wanshow' v

## Podcast Feed Files

A feed file, for use with the `--file` option, is a simple text file with one URL that leads to the RSS feed per line. 
The podcastdownloader will ignore all lines beginning with a hash (#), as well as empty lines to allow comments and a rudimentary structure if desired. 
Additionally, comments can be appended to the end of a line with a feed URL. 
As long as there is a space between the hash and the end of the URL, it will be removed when the file is parsed.
