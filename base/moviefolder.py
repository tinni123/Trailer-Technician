import os
import subprocess
from datetime import datetime
from base.nfo import NFO

from providers.tmdb import get_movie_info
from utils.logger import Logger


class Movie_Folder(object):
    log = Logger().get_log(__name__)
    min_movie_duration_sec = 600
    video_ext = ['.mkv', '.iso', '.wmv', '.avi', '.mp4', '.m4v', '.img', '.divx', '.mov', '.flv', '.m2ts']

    def __init__(self, directory):
        self.directory = directory
        self.movie_path = None
        self._trailer_path = None
        self._title = None
        self._year = None
        self._imdb_id = None
        self._tmdb_id = None
        self._tmdb_videos = None
        self._tmdb_queried = False
        self._parse_directory()

    @property
    def has_movie(self):
        if self.movie_path:
            return True
        else:
            return False

    @property
    def has_trailer(self):
        if self._trailer_path:
            return True
        else:
            return False

    @property
    def movie_filename(self):
        return os.path.basename(self.movie_path)

    @property
    def trailer_filename(self):
        if self._trailer_path:
            return os.path.basename(self._trailer_path)
        else:
            return os.path.splitext(os.path.basename(self.movie_path))[0] + '-trailer.mp4'

    @property
    def trailer_path(self):
        if self._trailer_path:
            return self._trailer_path
        else:
            return os.path.join(self.directory, self.trailer_filename)

    @property
    def title(self):
        # Get title from nfo
        if self._title:
            return self._title

        # Get tmdb title
        if not self._tmdb_queried:
            self.get_tmdb_data()

        # Return parsed title or None
        return self._title

    @property
    def year(self):
        # Get year from nfo
        if self._year:
            return self._year

        # Try to get year from tmdb
        if not self._tmdb_queried:
            self.get_tmdb_data()

        # Return parsed year or None
        return self._year

    @property
    def imdb_id(self):
        # Return nfo parsed imdb_id
        if self._imdb_id:
            return self._imdb_id

        # Try to get imdb id from tmdb
        if not self._tmdb_queried:
            self.get_tmdb_data()

        # Return parsed imdb or None
        return self._imdb_id

    @imdb_id.setter
    def imdb_id(self, imdb_id):
        self._imdb_id = imdb_id

    @property
    def tmdb_id(self):
        # Return nfo parsed id
        if self._tmdb_id:
            return self._tmdb_id

        # try tmdb for its id
        if not self._tmdb_queried:
            self.get_tmdb_data()

        # Return parsed tmdb id or None
        return self._tmdb_id

    @tmdb_id.setter
    def tmdb_id(self, tmdb_id):
        self._tmdb_id = tmdb_id

    @property
    def tmdb_videos(self):
        if not self._tmdb_videos:
            self.get_tmdb_data()

        return self._tmdb_videos

    def set_title_year(self, title, year):
        self._title = title
        self._year = year
        self._tmdb_id = None
        self._imdb_id = None
        self.get_tmdb_data()

    def get_tmdb_data(self):
        # Gather as much info as we can if no nfo was parsed
        if not self._title:
            self._get_title_from_directory()
        if not self._year:
            self._get_year_from_directory()
        if not self._imdb_id:
            self._get_imdb_from_filename()

        # Make a call to tmdb and gather info
        movie = get_movie_info(self._tmdb_id, self._imdb_id, self._year, self._title)
        if movie:
            self._tmdb_videos = movie['videos']['results']
            self._title = movie['title']
            self._year = str(datetime.strptime(movie['release_date'], '%Y-%m-%d').year)
            self._imdb_id = movie['imdb_id']
            self._tmdb_id = movie['id']
        
        # Indicate that tmdb has been queried 
        self._tmdb_queried = True

    def _get_year_from_directory(self):
        try:
            year = os.path.basename(self.directory).split('(')[1].split(')')[0].strip()
        except IndexError:
            self.log.debug('Could not parse year from "{}"'.format(os.path.basename(self.directory)))
            year = None
        
        return year

    def _get_title_from_directory(self):
        try:
            self._title = os.path.basename(self.directory).split('(')[0].strip()
        except IndexError:
            self.log.debug('Could not parse title from "{}"'.format(os.path.basename(self.directory)))

    def _get_imdb_from_filename(self):
        try:
            self._imdb_id = self.movie_filename.split('(')[1].split(')')[0].strip()
        except IndexError:
            self.log.debug('Could not parse imdb id from filename "{}"'.format(self.movie_filename))

    def _parse_videos(self, path):
        result = subprocess.run([
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of',
            'default=noprint_wrappers=1:nokey=1',
            path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
            )
        try:
            duration = float(result.stdout)
        except Exception as e:
            self.log.warning('Failed to determin video duration. Error: {}'.format(e))
            return False
        if duration >= self.min_movie_duration_sec:
            self.log.debug('Found movie file: "{}"'.format(os.path.basename(path)))
            self.movie_path = path
        else:
            self.log.debug('Found trailer file: "{}"'.format(os.path.basename(path)))
            self._trailer_path = path

    def _parse_nfo(self, path):
        nfo = NFO(path)
        if nfo.valid:
            self._title = nfo.title
            self._year = nfo.year
            self._imdb_id = nfo.imdb
            self._tmdb_id = nfo.tmdb
    
    def _parse_bdmv(self, path):
        if 'index.bdmv' in os.listdir(path):
            self.movie_path = os.path.join(path, 'index.bdmv')
            self._trailer_path = os.path.join(path, 'index-trailer.mp4')

    def _parse_video_ts(self, path):
        if 'VIDEO_TS' in os.listdir(path):
            self.movie_path = os.path.join(path, 'VIDEO_TS.ifo')
            self._trailer_path = os.path.join(path, 'VIDEO_TS-trailer.mp4')

    def _parse_directory(self):
        self.log.debug('Parsing "{}"'.format(self.directory))
        for item in os.listdir(self.directory):
            path = os.path.join(self.directory, item)
            if os.path.isfile(path):
                if os.path.splitext(path)[-1] in self.video_ext:
                    self._parse_videos(path)
                elif os.path.splitext(path)[-1] == '.nfo':
                    self._parse_nfo(path)
            elif os.path.isdir(path):
                if 'bdmv' in path.lower():
                    self.log.debug('Encounted a BluRay folder structure "{}"'.format(path))
                    self._parse_bdmv(path)
                elif 'video_ts' in path.lower():
                    self.log.debug('Encounterd a DVD folder structure "{}"'.format(path))
                    self._parse_video_ts(path)
