import hmac
import hashlib
import os
import subprocess
from flask import Blueprint, request, abort

webhook = Blueprint('webhook', __name__)

# Секретный ключ для проверки подписи от GitHub
WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET')

def is_valid_signature(payload_body, signature):
    """Проверка подписи от GitHub"""
    if not WEBHOOK_SECRET:
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@webhook.route('/webhook', methods=['POST'])
def handle_webhook():
    # Проверяем подпись
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature or not is_valid_signature(request.data, signature):
        abort(403)

    # Проверяем, что это push событие
    event = request.headers.get('X-GitHub-Event')
    if event != 'push':
        return 'OK', 200

    # Проверяем, что push был в main ветку
    payload = request.get_json()
    if payload['ref'] != 'refs/heads/main':
        return 'Not main branch', 200

    try:
        # Обновляем репозиторий
        repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        subprocess.run(['git', 'fetch', 'origin'], cwd=repo_path, check=True)
        subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=repo_path, check=True)
        
        return 'Repository updated successfully', 200
    except subprocess.CalledProcessError as e:
        return f'Error updating repository: {str(e)}', 500