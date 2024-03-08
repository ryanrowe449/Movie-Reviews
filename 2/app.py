#Ryan Rowe, rfr21, 2/21/2024
#The program in this file is the individual work of Ryan Rowe
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

#the GET method fetches addReview.html from server, and POST sends input data to server
@app.route('/addReview', methods=['GET', 'POST'])
def addReview():
    if request.method == 'POST':
        #if user presses submit, retrieve the data
        try:
            username = request.form['username']
            title = request.form['title']
            director = request.form['director']
            genre = request.form['genre']
            year = request.form['year']
            rating = request.form['rating']
            review = request.form['review']
            
            #parse for MovieID; takes first five chars of title, deletes spaces, appends year
            movieID = title[:5].replace(" ", "") + str(year)
            reviewTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with sqlite3.connect('movieData.db') as conn:
                cursor = conn.cursor()
                #insert the movie if it doesn't exist, ignore if it does
                cursor.execute("INSERT OR IGNORE INTO Movies(MovieID, Title, Director, Genre, Year) VALUES (?, ?, ?, ?, ?)", (movieID, title, director, genre, year))
                #insert review; no ignore because there can be multiple reviews for one movie
                cursor.execute("INSERT INTO Reviews(Username, MovieID, ReviewTime, Rating, Review) VALUES (?, ?, ?, ?, ?)", (username, movieID, reviewTime, rating, review))
                conn.commit()
        except Exception as e:
            #requirement: handle exceptions by rolling back
            print("An error occurred:", e)
            conn.rollback()
        #if the post works, go back to index page
        return redirect(url_for('index'))
    else:
        #if the user is not trying to POST yet, pull up addReview.html
        return render_template('addReview.html')

#same structure as addReview, different query
@app.route('/getYear', methods=['GET', 'POST'])
def getYear():
    if request.method == 'POST':
        year = request.form['year']
        with sqlite3.connect('movieData.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            #AvgRating is determined by AVG(Reviews.Rating), which works because the movies are grouped by MovieID
            #Joins movies with their reviews, filters them by year, orders in descending order of avgrating, and limits to 5
            cursor.execute("""
                SELECT Movies.Title, Movies.Year, Movies.Genre, AVG(Reviews.Rating) as AvgRating
                FROM Movies
                JOIN Reviews ON Movies.MovieID = Reviews.MovieID
                WHERE Movies.Year = ?
                GROUP BY Movies.MovieID
                ORDER BY AvgRating DESC
                LIMIT 5
            """, (year,))

            movies = cursor.fetchall()

        return render_template('bestInYear.html', movies=movies, year=year)
    else:
        return render_template('getYear.html')


@app.route('/bestInYear')
def bestInYear():
    return render_template('bestInYear.html')

@app.route('/listByGenre')
def listByGenre():
    return render_template('listByGenre.html')

@app.route('/getReviews', methods=['GET','POST'])
def getReviews():
    #fetch genre from user input in the form
    if request.method == 'POST':
        try:
            genre = request.form['genre']

            #can access data in the rows by column name
            with sqlite3.connect('movieData.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                #selects title and director from Movies table and review and rating from Reviews table
                #then JOINs rows from Movies and Reviews that have the same MovieID
                #filters out results that do not match the user-provided genre
                cursor.execute("""
                    SELECT Movies.Title, Movies.Director, Reviews.Review, Reviews.Rating
                    FROM Movies
                    JOIN Reviews ON Movies.MovieID = Reviews.MovieID
                    WHERE Movies.Genre = ?""", (genre,))
                movies = cursor.fetchall()
        except Exception as e:
            #requirement: handle exceptions by rolling back
            print("An error occurred:", e)
            conn.rollback()
            #passing data fetched (movies) to listByGenre.html to be rendered
        return render_template('listByGenre.html', movies=movies)
    else:
        #if the user is not trying to POST yet, pull up getReviews.html
        return render_template('getReviews.html')

if __name__ == '__main__':
    app.run(debug=True)