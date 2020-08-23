import os
from utils.logger import Logger
from utils.arguments import get_arguments
from utils.environment import get_environment

log = Logger().get_log('TrailerTechnician')

def _has_trailer(directory):
    # Check a directory for a file with '-trailer' in its name
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isfile(path):
            if '-trailer' in os.path.basename(path):
                return True

def _download_one(directory, title=None, year=None, imdb=None, tmdb=None):
    if _has_trailer(directory):
        log.info('Trailer found in "{}". Skipping download.'.format(directory))
        return True
    pass

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
        _download_one(os.path.dirname(env['movie_path']), env['title'], env['year'], env['imdbid'], env['tmdbid'])
    
    # Called without enough information to find appropriate trailer
    else:
        log.warning('Script called without enough valid information. Exiting')


if __name__ == '__main__':
    os.environ['radarr_eventtype'] = 'Download'
    # os.environ['radarr_moviefile_path'] = '/var/nfs/movies/8MM (1999)/8MM (tt0314273).mkv'
    os.environ['radarr_moviefile_path'] = 'm:/8MM (1999)/8MM (tt0134273).mkv'
    os.environ['radarr_movie_title'] = '8MM'
    os.environ['radarr_movie_year'] = '1999'
    os.environ['radarr_movie_imdbid'] = 'tt0134273'
    os.environ['radarr_movie_tmdbid'] = '8224'
    main()
