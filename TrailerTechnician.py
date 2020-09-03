import os
import sys
import shutil
import subprocess
from utils.logger import Logger
from utils.arguments import get_arguments
from utils.environment import get_environment
from base.moviefolder import Movie_Folder
from utils.config import get_config
from downloaders.apple import download_apple
from downloaders.youtube import download_youtube

log = Logger().get_log('TrailerTechnician')
config = get_config()
temp_dir = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloaders'), 'downloads')

def _download_trailer(directory):
    # directory is and instance of Movie_Folder

    success = False
    # Build temp directory and temp trailer file path
    if not os.path.isdir(temp_dir):
        log.info('Creating temp directory. "{}"'.format(temp_dir))
        os.mkdir(temp_dir)
        os.chmod(temp_dir, 0o777)
    temp_trailer_path = os.path.join(temp_dir, directory.trailer_filename)
    

    # Ensure title and year are parsed.
    if not directory.title and not directory.year:
        directory.get_tmdb_data()

    # search apple if we know title and year.
    if config['apple']['enabled'].lower() == 'true':
        if directory.title and directory.year and config['apple']['enabled'].lower() == 'true':
            success = download_apple(directory.year, directory.title, temp_trailer_path)
    else:
        log.debug('Apple download is disabled.')

    # Check youtube if nothing downloaded from apple
    if config['youtube']['enabled'].lower() == 'true':
        if not success and directory.tmdb_videos:
            success = download_youtube(directory.tmdb_videos, temp_trailer_path)
        else:
            log.warning('Could not parse data from TMDB. Skipping YouTube download.')
    else:
        log.debug('Youtube download is disabled.')

    if success:
        log.info('Moving trailer {} to "{}"'.format(temp_trailer_path, directory.directory))
        try:
            shutil.move(temp_trailer_path, directory.directory)
            log.info('Success!! Trailer has been moved to "{}"'.format(directory.directory))
        except Exception as e:
            log.warning('Could not move trailer to "{}" {}'.format(directory.directory, e))
        
        # Clean up temp directory
        for item in os.listdir(temp_dir):
            path = os.path.join(temp_dir, item)
            try:
                if os.path.isfile(path) or os.path.islink(path):
                    os.unlink(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
            except Exception as e:
                log.warning('Could not clean temp downloads folder "{}" ERROR: {}'.format(temp_dir, e))

def main():
    args = get_arguments()
    env = get_environment()

    # Called from cli, directory is required in this mode
    if args.directory:

        # Ensure path exists before continuing
        if not os.path.isdir(args.directory):
            log.critical('Directory not found. Exiting. "{}"'.format(args.directory))
            sys.exit(1)

        # Script called from cli with recursive flag set, ignore all other flags if this is set
        if args.recursive:
            log.info('Recursive mode enabled. Scanning "{}".'.format(args.directory))
            # Loop through each subdirectory
            for sub_dir in os.listdir(args.directory):
                path = os.path.join(args.directory, sub_dir)
                if os.path.isdir(path):
                    directory = Movie_Folder(path)
                    if directory.has_movie:
                        if not directory.has_trailer:
                            log.info('No Local trailer found in "{}"'.format(directory.directory))
                            _download_trailer(directory)
                        else:
                            log.info('Trailer already exists. "{}"'.format(directory.trailer_filename))
                    else:
                        log.warning('Assuming this is not a movie folder. No movie file found in "{}"'.format(directory.directory))
                    log.info('------------------------------------------------------')

        # Script called from cli without recursive flag set with directory only
        elif not args.year and not args.title:
            log.info('Single Directory mode enabled. Scanning "{}"'.format(args.directory))
            directory = Movie_Folder(args.directory)
            if directory.has_movie:
                if not directory.has_trailer:
                    log.info('No Local trailer found in "{}"'.format(directory.directory))
                    _download_trailer(directory)
                    log.info('------------------------------------------------------')
                else:
                    log.info('Trailer already exists. "{}"'.format(directory.trailer_filename))
                    log.info('------------------------------------------------------')
            else:
                log.info('Assuming this is not a movie folder. No movie file found in "{}"'.format(directory.directory))
                log.info('------------------------------------------------------')

        # Called from cli with year and title set
        elif args.title and args.year:
            # Start processing single directory from radarr env variables
            log.info('Single directory mode initiated for "{} ({})"'.format(args.title, args.year))
            directory = Movie_Folder(args.directory)
            directory.set_title_year(args.title, args.year)
            if directory.has_movie:
                if not directory.has_trailer:
                    log.info('No Local trailer found in {}'.format(directory.directory))
                    _download_trailer(directory)
                    log.info('------------------------------------------------------')
                else:
                    log.info('Trailer already exists. "{}"'.format(directory.trailer_filename))
            else:
                log.info('Assuming this is not a movie folder. No movie file found in "{}"'.format(directory.directory))

        # Called from cli with imdbid set
        elif args.imdbid:
            log.info('Single directory mode initiated for imdb "{}"'.format(args.imdbid))
            directory = Movie_Folder(args.directory)
            directory.imdb_id = args.imdbid
            if directory.has_movie:
                if not directory.has_trailer:
                    log.info('No Local trailer found in "{}"'.format(directory.directory))
                    _download_trailer(directory)
                    log.info('------------------------------------------------------')
                else:
                    log.info('Trailer already exists. "{}"'.format(directory.trailer_filename))
                    log.info('------------------------------------------------------')
            else:
                log.info('Assuming this is not a movie folder. No movie file found in "{}"'.format(directory.directory))
                log.info('------------------------------------------------------')

        # Called from cli with tmdbid set
        elif args.tmdbid:
            log.info('Single directory mode initiated for tmdb "{}"'.format(args.tmdbid))
            directory = Movie_Folder(args.directory)
            directory.tmdb_id = args.tmdbid
            if directory.has_movie:
                if not directory.has_trailer:
                    log.info('No Local trailer found for "{}" in {}'.format(directory.title, directory.year))
                    _download_trailer(directory)
                    log.info('------------------------------------------------------')
                else:
                    log.info('Trailer already exists. "{}"'.format(directory.trailer_filename))
            else:
                log.info('Assuming this is not a movie folder. No movie file found in "{}"'.format(directory.directory))

        # Not enough data was provided in arguments to process
        else:
            log.warning('Not enough info was provided. Exiting.')
            sys.exit(1)

    # Called from Radarr with environment variables set
    elif env['valid']:
        log.info('Single directory mode initiated from Radarr')

        # Ensure directory exists before continuing
        if not os.path.isdir(env['movie_dir']):
            log.warning('Directory not found. Exiting. "{}"'.format(env['movie_dir']))
            sys.exit(1)

        directory = Movie_Folder(env['movie_dir'], title=env['title'], year=env['year'], tmdb=env['tmdbid'], imdb=env['imdbid'])
        if directory.has_movie:
            if not directory.has_trailer:
                log.info('No Local trailer found in "{}"'.format(directory.directory))
                _download_trailer(directory)
                log.info('------------------------------------------------------')
            else:
                log.info('Trailer already exists. "{}"'.format(directory.trailer_filename))
                log.info('------------------------------------------------------')
        else:
            log.info('No movie file found in "{}"'.format(directory.directory))
            log.info('------------------------------------------------------')

    # Called without enough information to find appropriate trailer
    else:
        log.warning('Script called without enough valid information. Exiting')


if __name__ == '__main__':
    main()
