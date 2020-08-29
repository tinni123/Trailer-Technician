#!/usr/bin/env python3

import tmdbsimple as tmdb
from requests import HTTPError
from datetime import datetime
from utils.config import get_config
from utils.logger import Logger

config = get_config()
log = Logger().get_log(__name__)

# Find by tmdb id
def _find_by_tmdbid(tmdb_id):
    # Returns tmdb.Movies object
    try:
        movie = tmdb.Movies(tmdb_id)
    except HTTPError as e:
        _handle_error(e)
        return False

    try:
        data = movie.info(append_to_response='videos')
    except HTTPError as e:
        _handle_error(e)
        return False

    return data

# Find by imdbid
def _find_by_imdbid(imdb_id):
    # Returns tmdb.Movies object
    try:
        tmdb_id = tmdb.Find(imdb_id).info(external_source='imdb_id')['movie_results'][0]['id']
        movie = _find_by_tmdbid(tmdb_id)
    except HTTPError as e:
        _handle_error(e)
        return None

    return movie

# Find by title and year
def _find_by_title_year(title, year):
    # Returns tmdb.Movies object
    try:
        response = tmdb.Search().movie(query=title, year=year)
    except HTTPError as e:
        _handle_error(e)
        return False

     # Parse results. It may not be the correct search result
    for result in response['results']:
        if _release_date_to_year(result['release_date']) == year and result['title'].lower() == title.lower():
            return _find_by_tmdbid(result['id'])

    return False

# Handle http errors
def _handle_error(error):
    status_code = error.response.status_code
    if status_code == 401:
        log.error('TMDB API key was not accepted.')
    elif status_code == 404:
        log.warning('TMDB could not locate the requested resource')
    return

# Convert '2010-04-14' to '2010'
def _release_date_to_year(release_date):
    return str(datetime.strptime(release_date, '%Y-%m-%d').year)

# Main function to collect data about a movie
def get_movie_info(tmdb_id=None, imdb_id=None, year=None, title=None):
    tmdb.API_KEY = config['tmdb']['api_key']

    log.info('Getting data from TMDB.')

    # select how to search based on input data
    if tmdb_id:
        movie = _find_by_tmdbid(tmdb_id)
    elif imdb_id:
        movie = _find_by_imdbid(imdb_id)
    elif title and year:
        movie = _find_by_title_year(title, year)
    else:
        log.warning('Not enough info provided to find movie on TMDB')
        return False

    return movie
