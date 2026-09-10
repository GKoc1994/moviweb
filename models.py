from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """A MoviWeb user who keeps a list of favorite movies."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    movies = db.relationship("Movie", backref="user", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<User id={self.id} name={self.name!r}>"

    def __str__(self):
        return self.name


class Movie(db.Model):
    """A favorite movie that belongs to one user."""
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(200))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Movie id={self.id} name={self.name!r}>"

    def __str__(self):
        return f"{self.name} ({self.year})" if self.year else self.name
