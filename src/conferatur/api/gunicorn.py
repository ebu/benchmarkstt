"""
Entry point for a gunicorn server, serves at /api
"""

from .cli import create_app

application = create_app('/api', with_explorer=True)
