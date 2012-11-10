#!/bin/bash

FROM=IMDB
TO=MYIMDB
MYSQL_USER=$1
MYSQL_PASS=$2
TEMP_FILE=/tmp/imdb/create_schema.sql

run_sql() {
  mysql -u$MYSQL_USER -p$MYSQL_PASS < $TEMP_FILE
}
##############################################################################
cat <<END > $TEMP_FILE
USE $TO;
END
cat ../sql/schema.sql >> $TEMP_FILE
run_sql
##############################################################################
cat <<END > $TEMP_FILE
INSERT INTO MYIMDB.Genre (id,name)
SELECT id,name FROM IMDB.genre;
END
run_sql
##############################################################################
cat <<END > $TEMP_FILE
INSERT INTO MYIMDB.Movie (id,name,year,rating,votes)
SELECT mid,title,year,rating,num_votes 
FROM IMDB.movies
WHERE rating IS NOT NULL;
END
run_sql
##############################################################################
cat <<END > $TEMP_FILE
INSERT IGNORE INTO MYIMDB.Genres (genre_id, movie_id) 
SELECT gid, mid
FROM IMDB.movie_genre where mid in 
(SELECT mid FROM IMDB.movies WHERE rating IS NOT NULL);
END
run_sql
##############################################################################
##############################################################################
