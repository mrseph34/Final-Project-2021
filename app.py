from flask import Flask, render_template, json, jsonify, request, current_app as app
from datetime import date
import os
import requests
import sqlite3 as sql

app = Flask(__name__, static_folder="static")

con = sql.connect("./static/data/data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("fname" TEXT, "lname" TEXT, "email" TEXT, "password"  TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_posts" ("post" TEXT, "name" TEXT)')
con.commit()
cur.close()

@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/post/<email>/<fname>/<lname>', methods=['GET', 'POST'])
def post(email,fname, lname):
    post = request.form['post']
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    full_name = fname + " " + lname
    # cur.execute("INSERT INTO " + email.upper() + "(post, name) VALUES((?),(?))", (post, full_name))
    cur.execute("INSERT INTO all_posts(post, name) VALUES((?),(?))", (post, full_name))
    rows = cur.execute("SELECT * from all_posts")
    posts = []
    for row in rows:
        post = {'post' : row[0],'name' : row[1]}
        posts.append(post)

    con.commit()
    con.close()
        
    
    return render_template('posts.html', posts = posts)

@app.route('/register',methods = ['POST', 'GET'])
def register():
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']
    password = request.form['password']

    full_name = fname + " " + lname
    insert = '"' + email + '"'

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT email FROM users')

    emails = cur.fetchall()

    huh = "EMAIL DO NOT EXIST"

    for row in emails:
        if row[0].upper() == email.upper():
            huh = "EMAIL EXISTS"
            return render_template('index.html', failed2 = "Email already exists")
        
    if huh == "EMAIL DO NOT EXIST":
        cur.execute("INSERT INTO users(fname, lname, email, password) VALUES((?),(?),(?),(?))", (fname, lname, email, password))
        cur.execute('CREATE TABLE' + insert  + '("post" TEXT, "name" TEXT)')

        con.commit()

    cur.close()


    return render_template('create.html', email = email, fname = fname, lname = lname, created = huh)

@app.route('/signin',methods = ['POST', 'GET'])
def signin():
    name = ""
    email = request.form['email']
    password = request.form['password']

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users')

    all = cur.fetchall()
    
    exists = False

    for row in all:
        if row[2].upper() == email.upper():
            exists = True
            if row[3] == password:
                name = row[0]
            elif name != row[0]:
                return render_template('index.html', failed = "Password is incorrect")

    if exists == False:
            return render_template('index.html', failed = "Email is not registered")


    
    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (email,))
    fname = cur.fetchall()

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (email,))
    lname = cur.fetchall()



    

    cur.close()
    
    return render_template('home.html', fname = fname[0][0], email = email, lname = lname[0][0])


    

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 