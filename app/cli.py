# app/cli.py
import click
import os
from werkzeug.security import generate_password_hash
try:
    import sqlite3
except ImportError:
    import pysqlite3 as sqlite3
from app.db import get_db
from app.migrations.migration_runner import MigrationRunner


def register_cli_commands(app):
    """Регистрирует CLI команды с приложением."""
    
    @app.cli.command()
    @click.option('--login', prompt='Логин админа', default='admin')
    @click.option('--discriminator', prompt='Дискриминатор', default='0000')
    @click.password_option()
    def create_admin(login, discriminator, password):
        """Создать администратора системы"""
        from app.db import execute_insert
        
        try:
            # Создаем пользователя
            password_hash = generate_password_hash(password)
            user_id = execute_insert("""
                INSERT INTO users (login, discriminator, password_hash)
                VALUES (?, ?, ?)
            """, (login, discriminator, password_hash))
            
            # Назначаем роль admin
            execute_insert("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (?, (SELECT id FROM roles WHERE name = 'admin'))
            """, (user_id,))
            
            click.echo(f"✅ Администратор {login}#{discriminator} успешно создан!")
            
        except Exception as e:
            click.echo(f"❌ Ошибка: {e}")
    
    @app.cli.command()
    def migrate():
        """Применить миграции базы данных"""
        db_path = app.config.get('DATABASE_PATH', 'blog.db')
        runner = MigrationRunner(db_path)
        
        click.echo("🔄 Применение миграций...")
        pending = runner.get_pending_migrations()
        
        if not pending:
            click.echo("✅ Все миграции уже применены")
            return
        
        click.echo(f"📋 Найдено миграций: {len(pending)}")
        
        for migration_name in pending:
            click.echo(f"  📦 Применяем: {migration_name}")
            success = runner._apply_single_migration(migration_name)
            if not success:
                click.echo(f"❌ Ошибка при применении миграции {migration_name}")
                return
        
        click.echo("✅ Все миграции успешно применены")
    
    @app.cli.command()
    def migrate_upgrade():
        """Обновить схему базы данных (alias для migrate)"""
        # Вызываем ту же логику, что и migrate
        ctx = click.get_current_context()
        ctx.invoke(migrate)
    
    @app.cli.command()
    def seed():
        """Наполнить базу данных тестовыми данными"""
        from app.db import execute_query, execute_insert
        
        try:
            # Проверяем, есть ли уже данные
            existing_users = execute_query("SELECT COUNT(*) FROM users", fetch_one=True)
            if existing_users and existing_users.get('COUNT(*)', 0) > 0:
                click.echo("⚠️  В базе уже есть данные. Пропускаем наполнение.")
                return
            
            # Создаем тестового пользователя
            password_hash = generate_password_hash("test123")
            user_id = execute_insert("""
                INSERT INTO users (login, discriminator, password_hash)
                VALUES (?, ?, ?)
            """, ("testuser", "1234", password_hash))
            
            # Назначаем роль user
            execute_insert("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (?, (SELECT id FROM roles WHERE name = 'common'))
            """, (user_id,))
            
            # Создаем тестовые посты
            execute_insert("""
                INSERT INTO posts (title, body, user_id)
                VALUES 
                    ('Первый пост', 'Содержание первого тестового поста', ?),
                    ('Второй пост', 'Содержание второго тестового поста', ?)
            """, (user_id, user_id))
            
            click.echo("✅ Тестовые данные успешно добавлены")
            click.echo("👤 Пользователь: testuser#1234 (пароль: test123)")
            
        except Exception as e:
            click.echo(f"❌ Ошибка при наполнении базы: {e}")
    
    @app.cli.command()
    def db_reset():
        """Полностью сбросить и пересоздать базу данных"""
        db_path = app.config.get('DATABASE_PATH', 'blog.db')
        
        # Удаляем файл базы данных
        if os.path.exists(db_path):
            os.remove(db_path)
            click.echo(f"🗑️  Удален файл базы данных: {db_path}")
        
        # Применяем миграции
        click.echo("🔄 Применение миграций...")
        runner = MigrationRunner(db_path)
        
        pending = runner.get_pending_migrations()
        if pending:
            for migration_name in pending:
                click.echo(f"  📦 Применяем: {migration_name}")
                success = runner._apply_single_migration(migration_name)
                if not success:
                    click.echo(f"❌ Ошибка при применении миграции {migration_name}")
                    return
        
        click.echo("✅ База данных успешно пересоздана")
        
        # Наполняем тестовыми данными
        ctx = click.get_current_context()
        ctx.invoke(seed)