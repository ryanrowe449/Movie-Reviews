#Ryan Rowe, rfr21, 2/21/2024
#The program in this file is the individual work of Ryan Rowe
import sqlite3
#will be using a cursor for the whole project because it is 'better' practice
conn = sqlite3.connect('movieData.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE Reviews(Username TEXT, MovieID TEXT, ReviewTime DATETIME, Rating REAL, Review TEXT)')
cursor.execute('CREATE TABLE Movies(MovieID TEXT PRIMARY KEY, Title TEXT, Director TEXT, Genre TEXT, Year INTEGER)')
print("created both tables")
cursor.close()