import os
import shutil
from utils.logger import Logger
from utils.arguments import get_arguments
from utils.environment import get_environment
from providers.tmdb import TMDB
from downloaders.apple import download_apple
from downloaders.youtube import download_youtube

log = Logger().get_log('TrailerTechnician')
temp_dir = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloaders'), 'downloads')

def _has_trailer(movie_path):
    # Check a directory for a file with '-trailer' in its name
    for item in os.listdir(movie_path):
        path = os.path.join(movie_path, item)
        if os.path.isfile(path):
            if '-trailer' in os.path.basename(path):
                return True

def _build_temp_filepath(movie_path):
    # Ensure temp path exists
    if not os.path.isdir(temp_dir):
        log.debug('Creating temp directory for downloads.')
        os.mkdir(temp_dir)

    # Build full temp path
    filename = os.path.splitext(os.path.basename(movie_path))[0] + '.mp4'
    return os.path.join(temp_dir, filename)

# Move trailer to final directory
def _move_trailer(temp_path, movie_dir):
    log.info('Moving trailer to "{}"'.format(movie_dir))
    try:
        shutil.move(temp_path, movie_dir)
    except Exception as e:
        log.warning('Could not move trailer to "{}" {}'.format(movie_dir, e))

# Clean up downloads folder
def _clean_dir(temp_path):
    log.info('Cleaning up downloads directory.')
    for item in os.listdir(temp_path):
        path = os.path.join(temp_path, item)
        os.remove(path)

# Download a single trailer from either apple or youtube
def _download_one(movie_path, title=None, year=None, imdb=None, tmdb=None):
    movie_directory = os.path.dirname(movie_path)
    temp_file_path = _build_temp_filepath(movie_path)
    tmdb = None

    # Check if a trailer already exists
    if _has_trailer(movie_directory):
        log.info('Trailer found in "{}". Skipping download.'.format(movie_directory))
        return True

    # If no title or year was provided get it from tmdb
    if not title or year:
        tmdb = TMDB(tmdb, imdb, year, title)

    # Check Apple for a trailer to download
    if download_apple(year, title, temp_file_path):
        _move_trailer(temp_file_path, movie_directory)
        _clean_dir(temp_dir)
        return True

    # Get TMDB info if we haven't already
    if not tmdb:
        tmdb = TMDB(tmdb, imdb, year, title)

    # Check Youtube 
    if download_youtube(tmdb.tmdb_videos, temp_file_path):
        _move_trailer(temp_file_path, movie_directory)
        _clean_dir(temp_dir)
        return True
    
    # No trailer downloaded
    return False

def main():
    args = get_arguments()
    env = get_environment()

    # Script called from cli with recursive flag set
    if args.recursive and args.directory:
        log.info('Recursive mode enabled. Scanning "{}".'.format(args.directory))
        # Start Batch mode and collect trailers for each movie directory.
        # for sub_dir in os.listdir(args['directory']):
        #     path = os.path.join(args['directory'], sub_dir)
        #     if os.path.isdir(path):
        #         for item in os.listdir(path):
        #             if '-trailer.' in item:
        #                 log.debug('{}'.format(item))

    # Called from cli with year and title set
    elif args.year and args.title and args.directory:
        # Start processing single directory from radarr env variables
        log.info('Single directory mode initiated with title "{}" and year "{}"'.format(args.title, args.year))

    # Called from cli with tmdbid set
    elif args.tmdbid and args.directory:
        log.info('Single directory mode initiated with tmdb "{}"'.format(args.tmdbid))

    # Called from cli with imdbid set
    elif args.imdbid and args.directory:
        log.info('Single directory mode initiate with imdb "{}"'.format(args.imdbid))

    # Called from Radarr with environment variables set
    elif env['valid']:
        log.info('Single directory mode initiated from Radarr')

        # Download trailer for provided movie into provided path
        if _download_one(env['movie_path'], env['title'], env['year'], env['imdbid'], env['tmdbid']):
            log.info('Sucess! Trailer downloaded for "{}"'.format(env['title']))
    
    # Called without enough information to find appropriate trailer
    else:
        log.warning('Script called without enough valid information. Exiting')


if __name__ == '__main__':
    os.environ['radarr_eventtype'] = 'Download'
    # os.environ['radarr_moviefile_path'] = '/var/nfs/movies/8MM (1999)/8MM (tt0314273).mkv'
    os.environ['radarr_moviefile_path'] = 'm:/8MM (1999)/8MM (tt0134273).mkv'
    os.environ['radarr_movie_title'] = '8MM'
    # os.environ['radarr_movie_year'] = '1999'
    os.environ['radarr_movie_imdbid'] = 'tt0134273'
    # os.environ['radarr_movie_tmdbid'] = '8224'
    main()
