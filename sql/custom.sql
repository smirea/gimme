CREATE TABLE Movie (
    id integer NOT NULL PRIMARY KEY,
    name varchar(128) NOT NULL,
    year integer NOT NULL,
    rating real NOT NULL,
    votes integer NOT NULL,
    description text NOT NULL,
    imdb_url varchar(256) NOT NULL,
    picture_url varchar(256) NOT NULL
)
;
CREATE TABLE Taglines (
    movie_id integer NOT NULL REFERENCES Movie (id),
    tagline varchar(256) NOT NULL,
    UNIQUE (movie_id, tagline)
)
;
CREATE TABLE Genres (
    genre_id integer NOT NULL REFERENCES Genre (id),
    movie_id integer NOT NULL REFERENCES Movie (id),
    UNIQUE (genre_id, movie_id)
)
;
CREATE TABLE Genre (
    id integer NOT NULL PRIMARY KEY,
    name varchar(64) NOT NULL
)
;
CREATE TABLE Friends (
    id1 bigint NOT NULL,
    id2 bigint NOT NULL,
    UNIQUE (id1, id2)
)
;
CREATE TABLE User (
    fbid bigint NOT NULL PRIMARY KEY,
    fname varchar(128) NOT NULL,
    lname varchar(128) NOT NULL,
    email varchar(128) NOT NULL,
    fburl varchar(128) NOT NULL,
    picture varchar(128) NOT NULL,
    gender integer NOT NULL
)
;
CREATE TABLE Seen (
    id integer NOT NULL PRIMARY KEY,
    person_id bigint NOT NULL REFERENCES User (fbid),
    movie_id integer NOT NULL REFERENCES Movie (id),
    rating real NOT NULL,
    liked bool NOT NULL,
    review text
)
;
