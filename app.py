import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from sqlalchemy.exc import SQLAlchemyError

from data_manager import DataManager
from models import db, Movie

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "moviweb-dev-key")

basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, "data"), exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data', 'movies.db')}"

db.init_app(app)
data_manager = DataManager()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
OMDB_URL = "https://www.omdbapi.com/"


def fetch_movie_details(title):
    """Look up a movie on OMDb by title. Return a dict of details, or None."""
    if not OMDB_API_KEY:
        return None
    try:
        response = requests.get(OMDB_URL, params={"apikey": OMDB_API_KEY, "t": title}, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    if data.get("Response") != "True":
        return None

    year = data.get("Year", "")[:4]
    poster = data.get("Poster")
    director = data.get("Director")
    return {
        "name": data.get("Title", title),
        "director": director if director and director != "N/A" else None,
        "year": int(year) if year.isdigit() else None,
        "poster_url": poster if poster and poster != "N/A" else None,
    }


def get_user_or_404(user_id):
    """Return the user with the given id or stop with a 404 page."""
    user = data_manager.get_user(user_id)
    if user is None:
        abort(404)
    return user


def get_user_movie_or_404(user_id, movie_id):
    """Return a movie that belongs to the given user or stop with a 404 page."""
    movie = data_manager.get_movie(movie_id)
    if movie is None or movie.user_id != user_id:
        abort(404)
    return movie


@app.route("/")
def index():
    """Home page: show all users and a form to add a new one."""
    users = data_manager.get_users()
    return render_template("index.html", users=users)


@app.route("/users", methods=["POST"])
def create_user():
    """Add a new user from the form on the home page."""
    name = request.form.get("name", "").strip()
    if not name:
        flash("Please enter a name.", "error")
        return redirect(url_for("index"))
    try:
        data_manager.create_user(name)
        flash(f"User '{name}' was added.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("The user could not be saved. Please try again.", "error")
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/movies", methods=["GET"])
def list_movies(user_id):
    """Show the favorite movies of one user."""
    user = get_user_or_404(user_id)
    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", user=user, movies=movies)


@app.route("/users/<int:user_id>/movies", methods=["POST"])
def add_movie(user_id):
    """Add a movie to a user's favorites, with details from OMDb if available."""
    user = get_user_or_404(user_id)
    title = request.form.get("title", "").strip()
    if not title:
        flash("Please enter a movie title.", "error")
        return redirect(url_for("list_movies", user_id=user.id))

    details = fetch_movie_details(title)
    if details is None:
        year = request.form.get("year", "").strip()
        details = {
            "name": title,
            "director": request.form.get("director", "").strip() or None,
            "year": int(year) if year.isdigit() else None,
            "poster_url": None,
        }
        flash("No details found on OMDb, the movie was saved with the data you entered.", "info")

    try:
        data_manager.add_movie(Movie(user_id=user.id, **details))
        flash(f"'{details['name']}' was added to {user.name}'s movies.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("The movie could not be saved. Please try again.", "error")
    return redirect(url_for("list_movies", user_id=user.id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    """Change the title of a movie in a user's list."""
    get_user_movie_or_404(user_id, movie_id)
    new_title = request.form.get("title", "").strip()
    if not new_title:
        flash("The title cannot be empty.", "error")
        return redirect(url_for("list_movies", user_id=user_id))
    try:
        data_manager.update_movie(movie_id, new_title)
        flash(f"The title was changed to '{new_title}'.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("The movie could not be updated. Please try again.", "error")
    return redirect(url_for("list_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    """Remove a movie from a user's list."""
    movie = get_user_movie_or_404(user_id, movie_id)
    title = movie.name
    try:
        data_manager.delete_movie(movie_id)
        flash(f"'{title}' was deleted.", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("The movie could not be deleted. Please try again.", "error")
    return redirect(url_for("list_movies", user_id=user_id))


@app.errorhandler(404)
def page_not_found(error):
    """Show a friendly page when something does not exist."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """Show a friendly page when something goes wrong on the server."""
    return render_template("500.html"), 500


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
