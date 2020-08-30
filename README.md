# Trailer-Technician
A somewhat simple scripts to download movie trailers for your local library.  This can be called from [RADARR](https://github.com/Radarr/Radarr) applications as part of the post processing or from the CLI to process a single movie folder or an entire library at once.  Designed to operate with common naming conventions used in [Kodi](https://kodi.tv).  Many thanks to David and his work on [Trailer-Downloader](https://github.com/airship-david/Trailer-Downloader) where the core functionality of this script originates from.

## Requirements
-[FFmpeg](https://github.com/FFmpeg/FFmpeg)

-[Python 3.0+](https://www.python.org/)

-[requests](https://github.com/psf/requests)

-[tmdbsimple](https://github.com/celiao/tmdbsimple/blob/master/README.rst) + TMDB API Key

-[youtube-dl](https://github.com/rg3/youtube-dl/blob/master/README.md#installation)

-[unidecode](https://github.com/avian2/unidecode)

## Installation
1. Install [FFmpeg](https://github.com/FFmpeg/FFmpeg)

2. Install [Git](https://git-scm.com/downloads)

3. Install this script
In your command line navigate to a directory where RADARR has access to and run the following
```
git clone https://github.com/jsaddiction/Trailer-Technician.git
```

4. Install python requirements
While still in the command line navigate to the new directory /TrailerTechnician and run the following
```
sudo python3 -m pip3 install -r requirements.txt
```

5. Copy / rename settings.ini.example to settings.ini and configure your tmdb api key

## Settings
Settings are defined in settings.ini located in the root of this application.  If no options are specified then the default options are used.  TMDB api key is required for YouTube downloading and not having one will present some errors.

## Usage

### To download single trailer as part of RADARR post processing
Configure a 'Connection' in Radarr to call this script. The environment variables will be utilized to determine the appropriate trailer

### From the CLI
Make a call to this script making use of the following arguments.
```
-d directory            # Required - Path to movie directory
-r recursive mode       # Optional - Scan Subdirectories
-y year                 # Optional - Year of movie
-t title                # Optional - Title of movie
-imdb                   # Optional - Imdbid of movie
-tmdb                   # Optional - Tmdbid of movie
```

#### Example CLI calls
Get trailers for your entire library
```
python3 TrailerTechnician.py -rd "path/to/movielibrary"
```

Get trailer for single folder
```
python3 TrailerTechnician.py -d "path/to/movielibrary/movie (1999)"

python3 TrailerTechnician.py -d "path/to/movielibrary/movie (1999)" -t "Movie Title" -y 1999

python3 TrailerTechnician.py -d "path/to/movielibrary/movie (1999)" -tmdb 1234

python3 TrailerTechnician.py -d "path/to/movielibrary/movie (1999)" -imdb tt123456
```

### Library Structure
This script assumes the following structure.  The exact folder structure is not required but it does increase reliability and accuracy.

```
Movies
    Some Movie (2010)
        Some Movie File (tt123456).mkv
        Some Movie File-trailer.mp4
    Some other Movie (2011)
        Some other Movie File (tt654321).mkv
        some other Movie File-trailer.mp4
```

### How it works
This script if only given a directory via the CLI will process in the following manner.
1. Scan the directory for a trailer file, movie file and an nfo file.
2. If no movie file was found the directory is skipped since it can not determine the correct naming convention for the trailer.
3. The nfo file is parsed for data such as title, year, imdb id and tmdb id.
4. The video files, both movie and trailer, will be scanned with ffprobe to determine duration.
5. If no trailer file was found in the ffprobe step the data parsed from the nfo is passed to the download function.
6. The download function will first search Apple trailers for the appropriate trailer.
7. If no trailer was found then information parsed from TMDB is passed to youtube_dl.
8. Both download functions create temp files in the downloads directory of this script.
9. Once the downloading is complete the new trailer is moved to the destination directory and the downloads directory is cleaned up.

When called from the CLI in recursive mode the above process is repeated over each subdirectory of the path given.

When called from as a post processing script from RADARR without any arguments specified, the process above is also repeated this time using environment variables provided by RADARR.