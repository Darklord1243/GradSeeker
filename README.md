# GradSeeker

Discover your perfect Master's program. Compare requirements, calculate your compatibility, and shortlist your dream universities — all in one place.

**GradSeeker** is a Flask web application built for the XJCO2011 Web Application module (University of Leeds). It works like a shopping platform for graduate degrees: users browse programs by country, build a shortlist ("shopping cart"), and see algorithmic compatibility scores based on their academic profile ("The Wallet").

**Repository:** [github.com/Darklord1243/GradSeeker](https://github.com/Darklord1243/GradSeeker)

## Features

- **Hierarchical browsing** — Country → University → Program
- **User authentication** — Register, login, and manage a personal profile
- **Shortlist (many-to-many)** — Save programs to a personal shortlist across sessions
- **Compatibility calculator** — Algorithmic matching of user credentials vs. program requirements
- **Interactive world map** — Custom JavaScript map on the browse page
- **Accessible UI** — WCAG-oriented layout with custom CSS and partial Bootstrap use

## Tech Stack

- Python 3 / Flask
- SQLAlchemy + SQLite
- Flask-Login
- HTML, CSS, JavaScript (static assets in `static/`)
- pytest

## Project Structure

```
GradSeeker/
├── app.py              # Flask application factory and routes
├── models.py           # Database models and compatibility logic
├── load_data.py        # CSV → database loader
├── utils.py            # Shared helpers
├── run_dev.py          # Local development entry point
├── universities.csv    # Seed data
├── requirements.txt
├── static/
├── templates/
├── tests/
├── docs/
│   ├── SRS.md
│   ├── IMPLEMENTATION_PLAN.md
│   └── DEPLOYMENT_GUIDE.md
└── instance/           # SQLite database (created locally, not committed)
```

## Local Setup

### 1. Environment

```bash
conda activate xjco2011_env
cd GradSeeker
pip install -r requirements.txt
```

### 2. Initialize the database

```bash
python load_data.py
```

This creates `instance/database.db` and loads data from `universities.csv`.

### 3. Run the development server

```bash
python run_dev.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Running Tests

From the project root (`GradSeeker/`):

```bash
pytest
```

With coverage:

```bash
pytest --cov=. --cov-report=term-missing
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/SRS.md](docs/SRS.md) | Software Requirements Specification |
| [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) | RFC-style implementation plan |
| [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) | PythonAnywhere deployment guide |
| [docs/README.md](docs/README.md) | Documentation index |

## Deployment

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for step-by-step PythonAnywhere instructions.

## What Not to Commit

The following are generated locally and excluded via `.gitignore`:

- `__pycache__/` and `*.pyc`
- `instance/database.db` (SQLite database)
- `.pytest_cache/`, virtual environments, and `.env` files

## Author

LIN YUHAO — XJCO2011 Web Application, University of Leeds
