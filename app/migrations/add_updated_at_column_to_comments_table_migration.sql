--==================================================
-- Добавляем колонку updated_at без значения по умолчанию
ALTER TABLE comments ADD COLUMN updated_at TIMESTAMP;

-- Обновляем существующие записи updated_at текущим временем
UPDATE comments SET updated_at = CURRENT_TIMESTAMP;
--==================================================