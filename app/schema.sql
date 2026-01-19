DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;

CREATE TABLE user
(
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL,
    discriminator INTEGER NOT NULL,
    password      TEXT    NOT NULL,
    -- Уникальная комбинация логина и дискриминатора
    UNIQUE (username, discriminator)
);

CREATE TABLE post
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER   NOT NULL,
    created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title     TEXT      NOT NULL,
    body      TEXT      NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE comment
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER   NOT NULL,
    post_id   INTEGER   NOT NULL,
    created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    body      TEXT      NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (post_id) REFERENCES post (id)
);