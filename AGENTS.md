# Scripture stories
This repository presents illustrated scripture stories from The Church of Jesus Christ of Latter-day Saints as engaging slide presentations, with one slide per illustrated image for each story. It is optimized for responsive layouts to be great on mobile and desktop, and implements caching for offline availability and reduced network load.

# Backend
The `backend/` directory is a Python project with a FastAPI server for fetching and parsing the content. See `pyproject.toml` in that directory for information on the Python version and dependencies.

This repository uses `uv` for the Python project. For any Python commands, run them from the `backend` directory using `uv run`, e.g., `uv run python` to start a Python REPL within the project's virtual environment.

# Frontend
The frontend is a Vue.js application in `docs/index.html` (with caching implemented via a service worker in `docs/sw.js`). The `docs/` directory is the default for GitHub pages, which is why this repository is structured that way, and the `index.html` file is a single file defining styles, scripts, and content because it was started from within a chat session in Gemini, where the Canvas feature prioritizes single HTML files for simplified rendering. In the future, that file may be separated into content, scripts, and styling for easier maintenance and modularity.
