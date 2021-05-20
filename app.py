from flask import Flask, render_template, json, jsonify, request, current_app as app
from datetime import date
import os
import requests
import sqlite3 as sql

app = Flask(__name__, static_folder="static")
#comment
#comment2
con = sql.connect("data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("username"  TEXT, "password"  TEXT)')

print(cur.fetchall())

cur.close

@app.route('/')
def index():
 
    return render_template('index.html')

@app.route('/create',methods = ['POST', 'GET'])
def login():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

   

    return render_template('create.html', password = password, email = email, name = name)


    

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 