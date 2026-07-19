"""WSGI entrypoint for production (PythonAnywhere, etc.)."""

from app import create_app

app = create_app()
