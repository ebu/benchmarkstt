"""
Entry point for a gunicorn server, serves at /api
"""

from benchmarkstt.cli.entrypoints.api import create_app  # pragma: no cover
application = create_app('/api', with_explorer=True)  # pragma: no cover
