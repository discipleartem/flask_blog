-- Удаление таблиц в правильном порядке (сначала зависимые, потом основные)
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS user;

-- Таблица пользователей
CREATE TABLE user
(
    id            INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор пользователя
    username      TEXT    NOT NULL,                  -- Логин пользователя
    discriminator INTEGER NOT NULL,                  -- Дискриминатор (4-значный тег, как в Discord)
    password      TEXT    NOT NULL,                  -- Хэш пароля с солью
    -- Уникальная комбинация логина и дискриминатора
    UNIQUE (username, discriminator)
);

-- Таблица постов блога
CREATE TABLE post
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,                   -- Уникальный идентификатор поста
    author_id INTEGER   NOT NULL,                                  -- ID автора (внешний ключ на user)
    created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,        -- Дата и время создания
    title     TEXT      NOT NULL,                                  -- Заголовок поста
    body      TEXT      NOT NULL,                                  -- Содержимое поста
    FOREIGN KEY (author_id) REFERENCES user (id) ON DELETE CASCADE -- Удаление постов при удалении пользователя
);

-- Таблица комментариев к постам
CREATE TABLE comment
(
    id        INTEGER PRIMARY KEY AUTOINCREMENT,                    -- Уникальный идентификатор комментария
    author_id INTEGER   NOT NULL,                                   -- ID автора комментария
    post_id   INTEGER   NOT NULL,                                   -- ID поста, к которому оставлен комментарий
    created   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,         -- Дата и время создания
    body      TEXT      NOT NULL,                                   -- Текст комментария
    FOREIGN KEY (author_id) REFERENCES user (id) ON DELETE CASCADE, -- Удаление комментариев при удалении пользователя
    FOREIGN KEY (post_id) REFERENCES post (id) ON DELETE CASCADE    -- Удаление комментариев при удалении поста
);