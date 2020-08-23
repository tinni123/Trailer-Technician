from argparse import ArgumentParser
from __init__ import NAME, VERSION, DESCRIPTION

# Arguments
def get_arguments():
    parser = ArgumentParser(description=NAME+': '+DESCRIPTION)

    # Create a group for specific movie data
    movie_data = parser.add_argument_group('Movie Data')
    movie_data.add_argument('-y', '--year', help='Release year of the movie')
    movie_data.add_argument('-t', '--title', help='Movie title')
    movie_data.add_argument('-tmdb', '--tmdbid', help='TMDB id of the movie')
    movie_data.add_argument('-imdb', '--imdbid', help='IMDB id of the movie')
    parser.add_argument_group(movie_data)

    # Add all other arguments to the parser
    parser.add_argument('-v', '--version', action='version', version=NAME+' '+VERSION, help='Show the name and version number')
    parser.add_argument('-r', '--recursive', action='store_true', dest='recursive', help='Scan all directories within the path given')
    parser.add_argument('-d', '--directory', help='Full path to destination directory of the downloaded trailer', metavar='DIRECTORY')
    args = parser.parse_args()
    return args
