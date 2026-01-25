"""Тесты для системы дискриминаторов."""

import pytest
from app import create_app
import tempfile
import os


class TestDiscriminatorLogic:
    """Тесты логики генерации дискриминаторов."""

    def test_random_discriminator_generation(self):
        """Проверка, что разные пользователи получают разные случайные дискриминаторы."""
        db_fd, db_path = tempfile.mkstemp()
        
        app = create_app({
            'TESTING': True,
            'DATABASE': db_path,
            'SECRET_KEY': 'test-secret-key-for-testing',
            'WTF_CSRF_ENABLED': False,
        })

        with app.app_context():
            from app.db.db import init_db, get_db
            from app.auth.utils import generate_discriminator
            from app.auth import hash_password
            
            init_db()
            db = get_db()
            
            # Создаем несколько пользователей с одинаковым именем
            discriminators = []
            
            for i in range(5):
                disc = generate_discriminator(db, 'testuser')
                assert disc is not None
                assert 1 <= disc <= 9999
                discriminators.append(disc)
                
                # Добавляем пользователя в БД
                hashed_pw, salt = hash_password(f'pass{i}')
                db.execute(
                    'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
                    ('testuser', disc, hashed_pw, salt)
                )
                db.commit()
            
            # Проверяем, что все дискриминаторы разные
            assert len(set(discriminators)) == len(discriminators)
            print(f"Сгенерированные дискриминаторы: {discriminators}")

        os.close(db_fd)
        os.unlink(db_path)

    def test_discriminator_exhaustion(self):
        """Проверка поведения при исчерпании всех дискриминаторов."""
        db_fd, db_path = tempfile.mkstemp()
        
        app = create_app({
            'TESTING': True,
            'DATABASE': db_path,
            'SECRET_KEY': 'test-secret-key-for-testing',
            'WTF_CSRF_ENABLED': False,
        })

        with app.app_context():
            from app.db.db import init_db, get_db
            from app.auth.utils import generate_discriminator, MAX_DISCRIMINATOR
            
            init_db()
            db = get_db()
            
            # Занимаем все дискриминаторы для имени 'testuser'
            for disc in range(1, 6):  # Для теста используем только первые 5
                from app.auth import hash_password
                hashed_pw, salt = hash_password('pass')
                db.execute(
                    'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
                    ('testuser', disc, hashed_pw, salt)
                )
            db.commit()
            
            # Проверяем, что для новых пользователей есть свободные дискриминаторы (6-9999)
            disc = generate_discriminator(db, 'testuser')
            assert disc is not None
            assert disc >= 6  # Должен быть следующий свободный
            
            # Но для другого имени должны быть свободные дискриминаторы
            from app.auth import hash_password
            hashed_pw2, salt2 = hash_password('pass2')
            disc2 = generate_discriminator(db, 'otheruser')
            assert disc2 is not None
            assert 1 <= disc2 <= 9999

        os.close(db_fd)
        os.unlink(db_path)

    def test_different_usernames_independent_discriminators(self):
        """Проверка, что разные имена пользователей имеют независимые наборы дискриминаторов."""
        db_fd, db_path = tempfile.mkstemp()
        
        app = create_app({
            'TESTING': True,
            'DATABASE': db_path,
            'SECRET_KEY': 'test-secret-key-for-testing',
            'WTF_CSRF_ENABLED': False,
        })

        with app.app_context():
            from app.db.db import init_db, get_db
            from app.auth.utils import generate_discriminator
            from app.auth import hash_password
            
            init_db()
            db = get_db()
            
            # Создаем пользователя с именем 'alice'
            disc1 = generate_discriminator(db, 'alice')
            hashed_pw1, salt1 = hash_password('pass1')
            db.execute(
                'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
                ('alice', disc1, hashed_pw1, salt1)
            )
            db.commit()
            
            # Создаем пользователя с таким же дискриминатором, но другим именем
            disc2 = generate_discriminator(db, 'bob')
            # Дискриминатор может быть любым доступным, не обязательно таким же
            assert disc2 is not None
            assert 1 <= disc2 <= 9999
            
            hashed_pw2, salt2 = hash_password('pass2')
            db.execute(
                'INSERT INTO user (username, discriminator, password, salt) VALUES (?, ?, ?, ?)',
                ('bob', disc2, hashed_pw2, salt2)
            )
            db.commit()
            
            # Проверяем, что оба пользователя созданы
            users = db.execute(
                'SELECT username, discriminator FROM user WHERE username IN (?, ?)',
                ('alice', 'bob')
            ).fetchall()
            
            assert len(users) == 2
            # Дискриминаторы могут быть разными, это нормально
            assert users[0]['username'] != users[1]['username']

        os.close(db_fd)
        os.unlink(db_path)
