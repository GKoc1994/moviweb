from models import db, User, Movie


class DataManager:
    """Handles all database operations for MoviWeb."""

    def create_user(self, name):
        """Add a new user to the database and return it."""
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return user

    def get_users(self):
        """Return a list of all users, sorted by name."""
        return User.query.order_by(User.name).all()

    def get_user(self, user_id):
        """Return the user with the given id, or None."""
        return db.session.get(User, user_id)

    def get_movies(self, user_id):
        """Return a list of all movies of a specific user."""
        return Movie.query.filter_by(user_id=user_id).order_by(Movie.name).all()

    def get_movie(self, movie_id):
        """Return the movie with the given id, or None."""
        return db.session.get(Movie, movie_id)

    def add_movie(self, movie):
        """Add a new movie to a user's favorites and return it."""
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id, new_title):
        """Update the title of a movie. Return the movie, or None if it does not exist."""
        movie = self.get_movie(movie_id)
        if movie is None:
            return None
        movie.name = new_title
        db.session.commit()
        return movie

    def delete_movie(self, movie_id):
        """Delete a movie. Return True if it existed, otherwise False."""
        movie = self.get_movie(movie_id)
        if movie is None:
            return False
        db.session.delete(movie)
        db.session.commit()
        return True
