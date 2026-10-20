"""Entry point: `flask --app wsgi run` (dev) or `gunicorn wsgi:app` (production)."""
from siargao import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
