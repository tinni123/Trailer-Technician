#!/usr/bin/env python3

import os
from datetime import datetime
from utils.logger import Logger
try:
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et


class NFO(object):
    log = Logger().get_log(__name__)

    def __init__(self, path):
        self._title = None
        self._originaltitle = None
        self._imdb = None
        self._tmdb = None
        self._id = None
        self._year = None
        self._premiered = None
        self._uniqueids = []
        self._path = path
        self._parse()

    @property
    def valid(self):
        return self.title and self.year and self.imdb and self.tmdb

    @property
    def title(self):
        if self._title:
            return self._title
        elif self._originaltitle:
            return self._originaltitle
        else:
            return None

    @property
    def imdb(self):
        # First check in uniqueid list
        for item in self._uniqueids:
            if item['type'].lower() == 'imdb':
                return item['value']

        if self._imdb and self._imdb.startswith('tt') and len(self._imdb) == 9:
            return self._imdb

        # Revert to id tag
        if self._id and self._id.startswith('tt') and len(self._id) == 9:
            return self._id
        
        # if nothing was found return none
        return None

    @property
    def tmdb(self):
        # First check in uniquid list
        for item in self._uniqueids:
            if item['type'].lower() == 'tmdb':
                return item['value']
        
        if self._tmdb and not self._tmdb.startswith('tt'):
            return self._tmdb

        # Revert to id tag
        if self._id and not self._id.startswith('tt'):
            return self._id

        # If nothing was found return none
        return None

    @property
    def year(self):
        # Get the year first
        if self._year:
            if len(self._year) == 4 and self._year.isdigit():
                return self._year

        # Second try the premiered date
        elif self._premiered:
            return self._premiered_to_year(self._premiered)
        
        # Return None if we could not parse anything
        else:
            return None

    def _parse(self):
        # Parse the NFO
        self.log.debug('Parsing "{}"'.format(self._path))
        try:
            nfo = et.parse(self._path)
            root  = nfo.getroot()
        except IOError:
            self.log.warning('Could not open file "{}"'.format(self._path))
            self._valid = False
            return
        except et.ParseError:
            self.log.warning('Could not parse file "{}"'.format(self._path))
            self._valid = False
            return

        self._title = root.findtext('title')
        self._originaltitle = root.findtext('originaltitle')
        self._id = root.findtext('id')
        self._tmdb = root.findtext('tmdbid')
        self._imdb = root.findtext('imdbid')
        self._year = root.findtext('year')
        self._premiered = root.findtext('premiered')
        self._uniqueids = self._parse_uniqueids(root.findall('uniqueid'))
        self.log.debug('NFO Parsed: title="{}", year="{}", imdb_id="{}", tmdb_id="{}"'.format(self.title, self.year, self.imdb, self.tmdb))

    def _parse_uniqueids(self, uniqueid_list):
        uniqueids = []
        if len(uniqueid_list) == 0:
            return uniqueids
        for item in uniqueid_list:
            uniqueid = {}
            uniqueid['type'] = item.get('type')
            uniqueid['default'] = item.get('default')
            uniqueid['value'] = item.text
            uniqueids.append(uniqueid)
        return uniqueids

    def _premiered_to_year(self, release_date):
            return str(datetime.strptime(release_date, '%Y-%m-%d').year)