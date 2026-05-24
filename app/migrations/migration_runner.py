try:
    import sqlite3
except ImportError:
    import pysqlite3 as sqlite3
import os
import re
import logging
from typing import List, Tuple, Optional

class MigrationRunner:
    def __init__(self, db_path):
        self.db_path = db_path
        self.migrations_dir = "app/migrations"
        self.logger = logging.getLogger(__name__)



    def migrate_up(self):
        """Применяет все непримененные миграции"""
        try:
            applied_migrations = self.get_applied_migrations()
            all_migrations = self._get_migration_files()
            pending_migrations = self.get_pending_migrations()
            
            if not pending_migrations:
                return True
            
            for migration_name in pending_migrations:
                success = self._apply_single_migration(migration_name)
                if not success:
                    return False
            
            return True
            
        except Exception as e:
            return False



    def _apply_single_migration(self, migration_name: str) -> bool:
        """Применяет одну миграцию"""
        try:
            up_sql, down_sql = self.parse_migration_file(migration_name)
            if not up_sql:
                return False
            
            success = self.execute_migration(up_sql, migration_name)
            return success
            
        except Exception as e:
            return False



    def _get_migration_files(self) -> List[str]:
        """Получает отсортированный список файлов миграций"""
        if not os.path.exists(self.migrations_dir):
            return []
        
        files = []
        for filename in os.listdir(self.migrations_dir):
            if re.match(r'^\d{3}_[^.]+\.sql$', filename):
                # Извлекаем имя миграции без расширения
                migration_name = filename[:-4]  # Убираем .sql
                files.append(migration_name)
        
        # Сортируем по номеру
        files.sort(key=lambda x: int(x.split('_')[0]))
        return files



    def get_applied_migrations(self) -> List[str]:
        """Возвращает список примененных миграций"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT name FROM migrations 
                    ORDER BY name
                """)
                return [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Таблица migrations еще не существует
            return []




    def get_pending_migrations(self) -> List[str]:
        """Возвращает список непримененных миграций"""
        applied = set(self.get_applied_migrations())
        all_migrations = self._get_migration_files()
        
        pending = [m for m in all_migrations if m not in applied]
        return pending



    def parse_migration_file(self, migration_name: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Читает файл миграции и извлекает UP и DOWN SQL блоки.
        
        Returns:
            Tuple[up_sql, down_sql] - кортеж с SQL блоками или None
        """
        try:
            filepath = os.path.join(self.migrations_dir, f"{migration_name}.sql")
            
            if not os.path.exists(filepath):
                return None, None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем UP и DOWN блоки
            up_match = re.search(r'-- UP\s*\n(.*?)(?=-- DOWN|\Z)', content, re.DOTALL | re.IGNORECASE)
            down_match = re.search(r'-- DOWN\s*\n(.*?)\Z', content, re.DOTALL | re.IGNORECASE)
            
            up_sql = up_match.group(1).strip() if up_match else None
            down_sql = down_match.group(1).strip() if down_match else None
            
            if not up_sql:
                return None, None
            
            return up_sql, down_sql
            
        except Exception as e:
            return None, None



    def execute_migration(self, up_sql: str, migration_name: str) -> bool:
        """
        Выполняет UP блок SQL и записывает миграцию в таблицу migrations.
        
        Args:
            up_sql: SQL код для применения миграции
            migration_name: Имя миграции
            
        Returns:
            bool: True если успешно, False при ошибке
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Выполняем UP блок в транзакции
                conn.execute("BEGIN TRANSACTION")
                try:
                    # Выполняем миграцию
                    conn.executescript(up_sql)
                    
                    # Записываем миграцию в таблицу
                    conn.execute("""
                        INSERT INTO migrations (name) VALUES (?)
                    """, (migration_name,))
                    
                    conn.commit()
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    return False
                    
        except Exception as e:
            return False




    def execute_rollback(self, down_sql: str, migration_name: str) -> bool:
        """
        Выполняет DOWN блок SQL и удаляет миграцию из таблицы migrations.
        
        Args:
            down_sql: SQL код для отката миграции
            migration_name: Имя миграции
            
        Returns:
            bool: True если успешно, False при ошибке
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Выполняем DOWN блок в транзакции
                conn.execute("BEGIN TRANSACTION")
                try:
                    # Выполняем откат
                    conn.executescript(down_sql)
                    
                    # Удаляем миграцию из таблицы
                    conn.execute("""
                        DELETE FROM migrations WHERE name = ?
                    """, (migration_name,))
                    
                    conn.commit()
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    return False
                    
        except Exception as e:
            return False




    def migrate_down(self, target_migration: Optional[str] = None) -> bool:
        """
        Откатывает миграции.
        
        Args:
            target_migration: Если None, откат на 1 миграцию назад.
                            Если указана, откат к этой миграции.
                            
        Returns:
            bool: True если успешно, False при ошибке
        """
        try:
            applied_migrations = self.get_applied_migrations()
            
            if not applied_migrations:
                return True
            
            if target_migration:
                # Откат к конкретной миграции
                return self._rollback_to_migration(target_migration, applied_migrations)
            else:
                # Откат на 1 миграцию
                return self._rollback_one_migration(applied_migrations)
                
        except Exception as e:
            return False




    def _rollback_one_migration(self, applied_migrations: List[str]) -> bool:
        """Откатывает последнюю примененную миграцию"""
        last_migration = applied_migrations[-1]
        
        up_sql, down_sql = self.parse_migration_file(last_migration)
        if not down_sql:
            return False
        
        return self.execute_rollback(down_sql, last_migration)



    def _rollback_to_migration(self, target_migration: str, applied_migrations: List[str]) -> bool:
        """Откатывает к конкретной миграции"""
        if target_migration not in applied_migrations:
            return False
        
        # Находим индекс целевой миграции
        target_index = applied_migrations.index(target_migration)
        
        # Откатываем все миграции после целевой (в обратном порядке)
        migrations_to_rollback = applied_migrations[target_index + 1:]
        
        for migration_name in reversed(migrations_to_rollback):
            up_sql, down_sql = self.parse_migration_file(migration_name)
            if not down_sql:
                return False
            
            success = self.execute_rollback(down_sql, migration_name)
            if not success:
                return False
        
        return True