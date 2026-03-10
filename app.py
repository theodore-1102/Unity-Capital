"""Sutanto Capital — Development entry point."""

from app import create_app

app = create_app(mode="auto")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
