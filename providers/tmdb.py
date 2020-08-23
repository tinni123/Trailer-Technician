#!/usr/bin/env python3

import tmdbsimple as tmdb
from requests import HTTPError
from datetime import datetime
from utils.config import get_config
from utils.logger import Logger

config = get_config()

class TMDB(object):
    YOUTUBE_URL = 'https://www.youtube.com/watch?v='

    def __init__(self, tmdb_id=None, imdb_id=None, year=None, title=None):
        tmdb.API_KEY = config['tmdb']['api_key']
        self.log = Logger().get_log('TMDB_API')
        self.tmdb_id = tmdb_id
        self.imdb_id = imdb_id
        self.title = title
        self.year = year
        self.tmdb_videos = None
        self.get_movie_details()

    def _find_by_imdbid(self, imdb_id):
        # Find movie and return TMDBid
        try:
            response = tmdb.Find(imdb_id).info(external_source='imdb_id')
        except HTTPError as e:
            self._tmdb_error(e)
            return None
        self.tmdb_id = response['movie_results'][0]['id']
        self.title = response['movie_results'][0]['title']
        self.year = self._release_date_to_year(response['movie_results'][0]['release_date'])

    def _find_by_title_year(self, title, year):
        try:
            response = tmdb.Search().movie(query=self.title, year=self.year)
        except HTTPError as e:
            self._tmdb_error(e)
            return None

        # Parse results. It may not be the correct search result
        for result in response['results']:
            if self._release_date_to_year(result['release_date']) == self.year and result['title'].lower() == self.title.lower():
                self.tmdb_id = result['id']
                self.title = result['title']
                self.year = self._release_date_to_year(result['release_date'])

    def get_movie_details(self):
        # Get a tmdb_id first
        if not self.tmdb_id:

            # If no tmdbid was provided then try searching by imdbid
            if self.imdb_id:
                self._find_by_imdbid(self.imdb_id)

            # If no imdbid was provided then try searching by title and year
            elif self.title and self.year:
                self._find_by_title_year(self.title, self.year)

            # No tmdbid, imdbid, or title, year combo was provided. Can not continue.
            else:
                self.log.warning('Could not find movie details. Not enough info provided.')
                return

        # Get remaining movie details
        try:
            movie = tmdb.Movies(self.tmdb_id)
        except HTTPError as e:
            self._tmdb_error(e)
            return

        self.tmdb_videos = movie.videos()['results']

        # Only get extra data if none was provided.
        if not self.imdb_id or not self.tmdb_id or not self.title or not self.year:
            response = movie.info()
            self.imdb_id = response['imdb_id']
            self.tmdb_id = response['id']
            self.title = response['title']
            self.year = self._release_date_to_year(response['release_date'])

    def _release_date_to_year(self, release_date):
        return str(datetime.strptime(release_date, '%Y-%m-%d').year)

    def _tmdb_error(self, error):
        status_code = error.response.status_code
        if status_code == 401:
            self.log.error('TMDB API key was not accepted. Could not get details for "{} ({})"'.format(self.title, self.year))
        elif status_code == 404:
            self.log.warning('TMDB could not locate the requested resource "{} ({})"'.format(self.title, self.year))
        return
