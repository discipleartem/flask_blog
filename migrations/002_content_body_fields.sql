-- Replace posts.body / comments.body with body_source + body_format.
PRAGMA foreign_keys = ON;

ALTER TABLE posts ADD COLUMN body_source TEXT;
ALTER TABLE posts ADD COLUMN body_format TEXT NOT NULL DEFAULT 'plaintext';
UPDATE posts SET body_source = body WHERE body_source IS NULL;
ALTER TABLE posts DROP COLUMN body;

ALTER TABLE comments ADD COLUMN body_source TEXT;
ALTER TABLE comments ADD COLUMN body_format TEXT NOT NULL DEFAULT 'plaintext';
UPDATE comments SET body_source = body WHERE body_source IS NULL;
ALTER TABLE comments DROP COLUMN body;
