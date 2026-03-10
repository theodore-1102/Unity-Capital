"""Sutanto Capital — WSGI entry point (gunicorn / uWSGI)."""

from app import create_app

application = create_app(mode="auto")
