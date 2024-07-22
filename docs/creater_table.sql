/* drop table cascade */
--DROP TABLE IF EXISTS users CASCADE;

/* drop all tables */
DROP TABLE IF EXISTS
    users,
    words,
    users_words;

/* creating tables */
/* Table of users: */
CREATE TABLE IF NOT EXISTS Users (
    PRIMARY KEY (user_id),
    user_id INTEGER NOT NULL,
    first_name VARCHAR(50)  NOT NULL,
    last_name  VARCHAR(50)  NOT NULL
);



/* Table of words: */
CREATE TABLE IF NOT EXISTS Words (
    PRIMARY KEY (target_word),
    target_word    VARCHAR(50)  NOT NULL,
    translate_word VARCHAR(50)  NOT NULL,
    another_word1  VARCHAR(50),
    another_word2  VARCHAR(50),
    another_word3  VARCHAR(50)
);

/* Table of users_words: */
CREATE TABLE IF NOT EXISTS Users_words (
    PRIMARY KEY (user_id, target_word),
    user_id         INTEGER     NOT NULL REFERENCES users (user_id)
                                ON DELETE CASCADE ON UPDATE CASCADE,
    target_word     VARCHAR(50) NOT NULL REFERENCES words (target_word)
                                ON DELETE CASCADE ON UPDATE CASCADE,
    correct_answers INTEGER     DEFAULT 0 NOT NULL,
    wrong_answers   INTEGER     DEFAULT 0 NOT NULL
);
