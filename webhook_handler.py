import hmac
import hashlib
import os
import subprocess
from flask import Blueprint, request, abort, current_app

webhook = Blueprint('webhook', __name__)

@webhook.route('/webhook', methods=['POST'])
def handle_webhook():
    # Проверяем, что это push событие
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return 'OK', 200

    # Проверяем подпись от GitHub
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        abort(403)

    # Получаем секретный ключ из конфигурации
    webhook_secret = current_app.config.get('GITHUB_WEBHOOK_SECRET')
    if not webhook_secret:
        current_app.logger.error('GITHUB_WEBHOOK_SECRET not configured')
        abort(500)

    # Проверяем подпись
    expected_signature = 'sha256=' + hmac.new(
        webhook_secret.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        abort(403)

    # Проверяем, что push был в main ветку
    payload = request.get_json()
    if payload.get('ref') != 'refs/heads/main':
        return 'Not main branch', 200

    try:
        # Обновляем репозиторий
        repo_path = os.path.dirname(os.path.abspath(__file__))
        current_app.logger.info(f'Updating repository in {repo_path}')

        subprocess.run(['git', 'fetch', 'origin'], cwd=repo_path, check=True)
        subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=repo_path, check=True)

        current_app.logger.info('Repository updated successfully')
        return 'Repository updated successfully', 200
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f'Error updating repository: {str(e)}')
        return f'Error updating repository: {str(e)}', 500