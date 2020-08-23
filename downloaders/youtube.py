import youtube_dl
from utils.logger import Logger
from utils.config import get_config

log=Logger().get_log(__name__)
config = get_config()

# Download trailer from youtube
def download_youtube(tmdb_videos, filepath):

    youtube_url = 'https://www.youtube.com/watch?v='
    options = {
        'format': 'bestvideo[ext=mp4][height<='+config['youtube']['max_resolution']+']+bestaudio[ext=m4a]',
        'default_search': 'ytsearch1:',
        'restrict_filenames': 'TRUE',
        'prefer_ffmpeg': 'TRUE',
        'quiet': 'TRUE',
        'no_warnings': 'TRUE',
        'ignore_errors': 'TRUE',
        'no_playlist': 'TRUE',
        'outtmpl': filepath
    }

    # Filter tmdb videos based on settings and video types
    links = []
    for video in tmdb_videos:
    # Filter only trailer videos
        if not video['type'].lower() == 'trailer':
            continue
        # Filter results based on language that user may have provided
        if config['youtube']['lang'] and not video['iso_639_1'].lower() == config['youtube']['lang']:
            continue
        # Filter results based on resolution that user may have provided
        if config['youtube']['min_resolution'] and not video['size'] >= int(config['youtube']['min_resolution']):
            continue
        # filter only youtube trailers
        if not video['site'].lower() == 'youtube':
            continue
        
        links.append('{}{}'.format(youtube_url, video['key']))

    # Check if any links to parse
    if len(links) == 0:
        log.info('No YouTube trailers parsed from TMDB. Skipping YouTube download.')
        return False
    log.info('Found {} trailers listed on TMDB.'.format(len(links)))

    # Loop through links until one works
    for link in links:
        try:
            # Attemp to download the video
            with youtube_dl.YoutubeDL(options) as youtube:
                log.info('Attempting to download video at "{}". Please Wait...'.format(link))
                if youtube.extract_info(link, download=True):
                    log.info('Download complete!')
                    return True
        except Exception as e:
            log.warning('Something went wrong while downloading. {}'.format(e))
    return False
