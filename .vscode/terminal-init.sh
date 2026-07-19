# Загружается как --rcfile для integrated terminal (см. .vscode/settings.json).
# Активирует .venv без печати команды source в скроллбеке.
if [ -f "$HOME/.bashrc" ]; then
  # shellcheck source=/dev/null
  . "$HOME/.bashrc"
fi

_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$_ROOT/.venv/bin/activate" ]; then
  # shellcheck source=/dev/null
  . "$_ROOT/.venv/bin/activate"
fi
unset _ROOT
