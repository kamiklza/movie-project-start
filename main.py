from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

moviedb_endpoint = "https://api.themoviedb.org/3/search/movie"
api_key = "5e4a8bfa724288cbccad7800c4b3c989"





app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

db.create_all()

class UpdateForm(FlaskForm):
    rating = StringField('Your Rating Out of 10 (e.g 7.8)', validators=[DataRequired()])
    review = StringField('Your Review', validators=[DataRequired()])
    submit = SubmitField('Done')


class AddForm(FlaskForm):
    title = StringField('Movie Title')
    add = SubmitField('Add Movie')

# movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.session.add(movie)
# db.session.commit()


@app.route("/")
def home():
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)


@app.route('/edit/<movie_id>', methods=["GET", "POST"])
def update(movie_id):
    update_form = UpdateForm()
    if update_form.validate_on_submit() and request.method == "POST":
        rating = update_form.rating.data
        review = update_form.review.data
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = rating
        movie_to_update.review = review
        db.session.commit()
        return redirect(url_for('home'))
    selected_movie = Movie.query.get(movie_id)
    return render_template('edit.html', movie=selected_movie, form=update_form)

@app.route('/add', methods=["GET", "POST"])
def add():
    add_form = AddForm()
    if request.method == "POST":
        print(add_form.title.data)
        params = {
            "api_key": api_key,
            "query": add_form.title.data
        }

        response = requests.get(url=moviedb_endpoint, params=params)
        print(response.json())
        return render_template('select.html', movies=response.json()["results"])
    return render_template('add.html', form=add_form)

@app.route('/delete')
def delete():
    movie_id = request.args.get('movie_id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/update')
def add_card():
    movie_id = request.args.get('movie_id')
    endpoint = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": api_key
    }
    response = requests.get(url=endpoint, params=params)
    movie = response.json()
    movie_to_add = Movie(title=movie['original_title'], img_url=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}", year=movie['release_date'], description=movie['overview'], rating="None", ranking="None", review="None")
    db.session.add(movie_to_add)
    db.session.commit()
    return redirect(url_for('home'))






# @app.route('/edit/<movie_id>', methods=["GET", "POST"])
# def update(movie_id):
#     if request.method == "POST":
#         rating = request.form["rating"]
#         review = request.form["review"]
#         movie_to_update = Movie.query.get(movie_id)
#         movie_to_update.rating = rating
#         movie_to_update.review = review
#         db.session.commit()
#         return redirect(url_for('home'))
#     selected_movie = Movie.query.get(movie_id)
#     return render_template('edit.html', movie=selected_movie)


if __name__ == '__main__':
    app.run(debug=True)
