import os


def get_environment():
    env = {
        'valid': False,
        'download_event': os.environ.get('radarr_eventtype', '').lower() == 'download',
        'title': os.environ.get('radarr_movie_title'),
        'year': os.environ.get('radarr_movie_year'),
        'imdbid': os.environ.get('radarr_movie_imdbid'),
        'tmdbid': os.environ.get('radarr_movie_tmdbid'),
        'movie_dir': os.path.abspath(os.environ.get('radarr_movie_path', '')),
    }
    
    # Check if it was a download event from Radarr and valid file path was provided.
    if env['download_event']:
        
        # Check if path provided is a valid path
        if os.path.isdir(env['movie_dir']):

            # Check if title and year were provided
            if env['title'] and env['year']:
                env['valid'] = True

            # Check if imdb or tmdb id was provided
            if env['imdbid'] or env['tmdbid']:
                env['valid'] = True

    return env
