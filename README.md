# Trailer-Technician
A somewhat simple scripts to download movie trailers for your local library.  This can be called from [RADARR](https://github.com/Radarr/Radarr) applications as part of the post processing or from the CLI to process a single movie folder or an entire library at once.  Designed to operate with common naming conventions used in [Kodi](https://kodi.tv).

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
```
git clone https://github.com/jsaddiction/Trailer-Technician.git
```

4. Install python requirements
```
sudo python3 -m pip3 install -r requirements.txt
```

5. Copy / rename settings.ini.example to settings.ini and configure your tmdb api key

## Settings
Settings are defined in settings.ini located in the root of this application.  If no options are specified then the default options are used.  TMDB api key is not required however, not having one severly limits acuracy and functionality.

## Usage

### To download single trailer as part of post processing
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