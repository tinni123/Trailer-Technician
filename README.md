# Trailer-Technician
A simple package of scripts to download movie trailers for your local library.  This can be called from your downloading applications as part of the post processing or in bulk mode from the CLI to process an entire library at once.  Designed to operate with common naming conventions used in [Kodi](https://kodi.tv).

## Requirements
-[FFmpeg](https://github.com/FFmpeg/FFmpeg)

-[Python 3.0+](https://www.python.org/)

-[requests](https://github.com/psf/requests)

-[tmdbsimple](https://github.com/celiao/tmdbsimple/blob/master/README.rst) + TMDB API Key

-[youtube-dl](https://github.com/rg3/youtube-dl/blob/master/README.md#installation)

-[unidecode](https://github.com/avian2/unidecode)

## Installation
1. Install [FFmpeg](https://github.com/FFmpeg/FFmpeg)

2. Install python requirements
```
sudo python3 -m pip3 install -r requirements.txt
```

## Settings
Settings are assembled as a dict and passed to the instantiation of the object.  If no options are specified then the default options are used.  TMDB api key is required.
```
tmdb_api_key=1234567abcdef,
options = {
    'min_resolution': 720,              # Default: 720
    'max_resolution': 1080,             # Default: 1080
    'custom_directory': '',             # Default: None
    'language': 'en',                   # Default: en
}
```

## Usage

### To download single trailer as part of post processing
Configure a 'Connection' in Radarr to call this script. The environment variables will be utilized to determin the appropriate trailer

### To download trailers for each of your movies in your library
Using your CLI make a call to this script making use of the following arguments.
```
-a your_tmdb_api_key                        # Required
-d directory_containing_movie_directories   # Required
-h maximum_resolution                       # Optional
-m minimum_resolution                       # Optional
-l language                                 # Optional
```

#### Library Structure
This script assumes the following structure and may not work correctly if structured otherwise.  Year and IMDB ids are not required in the paths below.

```
Movies
    Some Movie (2010)
        Some Movie File (tt123456).mkv
        Some Movie File-trailer.mp4
    Some other Movie (2011)
        Some other Movie File (tt654321).mkv
        some other Movie File-trailer.mp4
```