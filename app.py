from flask import Flask, render_template, json, jsonify, request, current_app as app
from datetime import date
import os
import requests
import sqlite3 as sql

app = Flask(__name__, static_folder="static")

con = sql.connect("static/data/data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("name" TEXT, "email" TEXT, "password"  TEXT)')
cur.execute('SELECT email FROM users')
print(cur.fetchall())

cur.close()

@app.route('/')
def index():
 
    return render_template('index.html')

@app.route('/register',methods = ['POST', 'GET'])
def register():
    con = sql.connect("static/data/data.db")
    cur = con.cursor()
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

   # cur.execute("INSERT INTO users(name,email,password) VALUES((?),(?),(?))", (name, email, password))

    cur.execute('SELECT email FROM users')

    emails = cur.fetchall()
    print(cur.fetchall())
    huh = "EMAIL DO NOT EXIST"

    for row in emails:
        if row == email:
            huh = "EMAIL EXISTS"
        
    #if huh == False:
       # cur.execute("INSERT INTO users(name,email,password) VALUES((?),(?),(?))", (name, email, password))

    cur.close()

    return render_template('index.html', email = email, name = name, created = huh)


    

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 