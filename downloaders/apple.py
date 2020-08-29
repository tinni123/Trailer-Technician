import os
import shutil
import json
import socket
import html.parser
import unicodedata
from unidecode import unidecode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from utils.logger import Logger
from utils.config import get_config

trailer_url = 'https://trailers.apple.com/'
log = Logger().get_log(__name__)
config = get_config()

# Match titles
def _matchTitle(title):
    return unicodedata.normalize('NFKD', _removeSpecialChars(title).replace('/', '').replace('\\', '').replace('-', '').replace(':', '').replace('*', '').replace('?', '').replace("'", '').replace('<', '').replace('>', '').replace('|', '').replace('.', '').replace('+', '').replace(' ', '').lower()).encode('ASCII', 'ignore')

# Remove special characters
def _removeSpecialChars(query):
    return ''.join([ch for ch in query if ch.isalnum() or ch.isspace()])

# Remove accent characters
def _removeAccents(query):
    return unidecode(query)

# Unescape characters
def _unescape(query):
    return html.unescape(query)

# Load json from url
def _loadJson(url):
    response = urlopen(url)
    str_response = response.read().decode('utf-8')
    return json.loads(str_response)

# Map resolution
def _mapRes(res):
    res_mapping = {'480': u'sd', '720': u'hd720', '1080': u'hd1080'}
    if res not in res_mapping:
        res_string = ', '.join(res_mapping.keys())
        raise ValueError('Invalid resolution. Valid values: %s' % res_string)
    return res_mapping[res]

# Convert source url to file url
def _convertUrl(src_url, res):
    src_ending = '_%sp.mov' % res
    file_ending = '_h%sp.mov' % res
    return src_url.replace(src_ending, file_ending)

# Get file urls
def _getUrls(page_url, res):
    urls = []
    film_data = _loadJson(page_url + '/data/page.json')
    title = film_data['page']['movie_title']
    apple_size = _mapRes(res)

    for clip in film_data['clips']:
        video_type = clip['title']
        if apple_size in clip['versions']['enus']['sizes']:
            file_info = clip['versions']['enus']['sizes'][apple_size]
            file_url = _convertUrl(file_info['src'], res)
            video_type = video_type.lower()
            if (video_type.startswith('trailer')):
                url_info = {
                    'res': res,
                    'title': title,
                    'type': video_type,
                    'url': file_url,
                }
                urls.append(url_info)

    final = []
    length = len(urls)

    if length > 1:
        final.append(urls[length-1])
        return final
    else:
        return urls

# Download the file
def _downloadFile(url, filepath):
    data = None
    headers = {'User-Agent': 'Quick_time/7.6.2'}
    req = Request(url, data, headers)
    chunk_size = 1024 * 1024

    try:
        server_file_handle = urlopen(req)
    except HTTPError as e:
        log.warning('Encountered HTTP error from apple. {}'.format(e))
        return False
    except URLError as e:
        log.warning('Encountered URL error from apple. {}'.format(e))
        return False

    log.info('Attempting to download Apple trailer from {}'.format(url))
    
    try:
        with open(filepath, 'wb') as local_file_handle:
            shutil.copyfileobj(server_file_handle, local_file_handle, chunk_size)
            log.info('Download Complete!')
            return True
    except socket.error as e:
        log.warning('Encountered Socket error from apple. {}'.format(e))
        return False

# Search Apple
def _searchApple(query):
    query = _removeSpecialChars(query)
    query = _removeAccents(query)
    query = query.replace(' ', '+')
    search_url = 'https://trailers.apple.com/trailers/home/scripts/quickfind.php?q='+query
    return _loadJson(search_url)

def download_apple(year, title, filepath):
# Search Apple
        search = _searchApple(title)

        # Check search results and see if we need to continue.
        if len(search['results']) == 0:
            log.info('No trailers found on Apple.')
            return False

        log.info('Found {} Apple trailers for "{}"'.format(len(search['results']), title))

        # Parse search results
        for result in search['results']:

            # Filter by year and title
            if 'releasedate' in result and 'title' in result:
                if year.lower() in result['releasedate'].lower() and _matchTitle(title) == _matchTitle(_unescape(result['title'])):
                    links = _getUrls(trailer_url+result['location'], config['apple']['resolution'])
                    for link in links:
                        if _downloadFile(link['url'], filepath):
                            return True
        # return false if no trailer was downloaded
        return False