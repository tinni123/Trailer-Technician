import pprint
from providers.tmdb import get_movie_info

# movie = get_movie_info(tmdb_id='9255')
# movie = get_movie_info(imdb_id='tt0107144')
movie = get_movie_info(title='Hot Shots! Part Deux', year='1993')
pprint.pprint(movie)