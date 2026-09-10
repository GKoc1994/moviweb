# MoviWeb

A Flask web app where users manage their favorite movies. Data is stored in SQLite through Flask-SQLAlchemy; movie details (director, year, poster) are loaded from the OMDb API.

## Features

- Home page with all users and a form to add a new user
- Movie list per user, with poster, director and year
- Add a movie by title (details fetched from OMDb, manual fallback if not found)
- Update a movie title and delete a movie
- Friendly 404 and 500 error pages, input validation and flash messages

## Project structure

    app.py            Flask routes and OMDb lookup
    data_manager.py   DataManager class with all database operations
    models.py         SQLAlchemy models: User and Movie
    templates/        Jinja2 templates (base, index, movies, 404, 500)
    static/style.css  Styling
    data/             SQLite database (created on first run)

## Run it

    pip install -r requirements.txt
    cp .env.example .env      # then add your OMDb API key
    python3 app.py

The app runs on port 5000. Get a free OMDb key at https://www.omdbapi.com/apikey.aspx.
