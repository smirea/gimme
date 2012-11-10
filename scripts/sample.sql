INSERT IGNORE INTO MYIMDB.Genres (genre_id, movie_id) 
SELECT gid, mid
FROM IMDB.movie_genre where mid in 
(SELECT mid FROM IMDB.movies WHERE rating IS NOT NULL);
