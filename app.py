from flask import Flask, redirect, flash, render_template, json, jsonify, request, current_app as app
from datetime import date, datetime
import os
import requests
import sqlite3 as sql
import urllib.request
from werkzeug.utils import secure_filename
import datetime

PROFILE_FOLDER = 'static/profile/'
POSTS_FOLDER = 'static/posts/'

today = date.today()

app = Flask(__name__, static_folder="static")

con = sql.connect("./static/data/data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("fname" TEXT, "lname" TEXT, "email" TEXT, "password"  TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_posts" ("post" TEXT, "title" TEXT, "date" TEXT, "name" TEXT, "description" TEXT, "likes" TEXT, "likesAmount" INTEGER, "comments" TEXT, "email" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_comments" ("id", "name", "comment", "date","email")')
con.commit()
cur.close()

app.secret_key = "secret key"
app.config['POSTS_FOLDER'] = PROFILE_FOLDER
app.config['POSTS_FOLDER'] = POSTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

loggedin = False
loggedinEmail = ""
full_name = ""


@app.route('/')
def index():
    global loggedin
    if loggedin:
        return redirect("/home", code=302)
    return render_template('index.html')

@app.route('/home')
def home():
    global loggedinEmail
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        posts.append(post)
    cur.close()
    
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT * from all_comments")
    rowes = cur.fetchall()
    comments = []
    for row in rowes:
        comment = [row[0],row[1],row[2],row[3],row[4]]
        comments.append(comment)
    cur.close()

    return render_template('home.html', posts = posts, comments=comments, replies="replies", name=full_name, email=loggedinEmail)

@app.route('/post', methods=['GET', 'POST'])
def post():
    global loggedin
    global loggedinEmail
    global full_name
    email = loggedinEmail

    if loggedin == False:
        print("NOT LOGGED IN")
        return redirect("/", code=302)

    img = request.files['img']
    if img.filename != "":
        print(img.filename)
        filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['POSTS_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')

    title = request.form.get("title", False)
    description = request.form.get("description", False)
    #day = today.strftime("%B %d, %Y")
    date = datetime.datetime.now()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email) VALUES((?),(?),(?),(?),(?),(?),(?),(?),(?))", (img.filename, title, date, full_name, description, "[]", 0, "[]", email))
    #cur.execute("INSERT INTO " + email.upper() + "(post, name) VALUES((?),(?))", (post, full_name))
    #cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email) VALUES((?),(?))", (post, full_name))
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        posts.append(post)

    con.commit()
    con.close()
        
    
    return render_template('home.html', posts = posts, email=loggedinEmail)

@app.route('/register',methods = ['POST', 'GET'])
def register():
    global loggedin
    global loggedinEmail
    global full_name
    if loggedin:
        return redirect("/home", code=302)

    fname = request.form.get('fname', False)
    lname = request.form.get('lname', False)
    email = request.form.get('email', False)
    password = request.form.get('password', False)

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

        loggedin = True
        loggedinEmail = email
        con.commit()

    cur.close()


    return render_template('create.html', email = email, fname = fname, lname = lname, created = huh)

@app.route('/signin',methods = ['POST', 'GET'])
def signin():
    global loggedin
    global loggedinEmail
    global full_name

    if loggedin:
        return redirect("/home", code=302)

    name = ""
    email = request.form.get('email', False)
    password = request.form.get('password', False)

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
                loggedin = True
                loggedinEmail = email
                
            elif name != row[0]:
                return render_template('index.html', failed = "Password is incorrect")

    if exists == False:
            return render_template('index.html', failed = "Email is not registered")


    
    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (email,))
    fname = cur.fetchall()
    fname = fname[0][0]

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (email,))
    lname = cur.fetchall()
    lname = lname[0][0]

    full_name = fname+" "+lname

    cur.close()
    
    return render_template('home.html', fname = fname[0][0], email = email, lname = lname[0][0])

@app.route('/like/<id>',methods = ['POST', 'GET'])
def like(id):
    global loggedin
    global loggedinEmail
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        posts.append(post)
    cur.close()
    for post in posts:
        if id == post[2]:
            if ","+loggedinEmail not in post[5]:
                con = sql.connect("./static/data/data.db")
                cur = con.cursor()
                cur.execute("UPDATE all_posts SET likesAmount=likesAmount+1 WHERE date='"+post[2]+"'")
                cur.execute("UPDATE all_posts SET likes=trim(',"+loggedinEmail+"') WHERE date='"+post[2]+"'")
                con.commit()

                cur.close()
                return "successDrop"
                
            con = sql.connect("./static/data/data.db")
            cur = con.cursor()
            cur.execute("UPDATE all_posts SET likesAmount=likesAmount-1 WHERE date='"+post[2]+"'")
            cur.execute("UPDATE all_posts SET likes=likes+',"+loggedinEmail+"' WHERE date='"+post[2]+"'")
            con.commit()

            cur.close()
    return "success", 200

@app.route('/comment/<comment>/<id>',methods = ['POST', 'GET'])
def comments(comment,id):
    global loggedinEmail
    global full_name

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    date = datetime.datetime.now()

    cur.execute("INSERT INTO all_comments(id, name, comment, date, email) VALUES((?),(?),(?),(?),(?))", (id, full_name, comment, date, loggedinEmail))
    con.commit()

    cur.close()

    return "success", 200


@app.route('/logout',methods = ['POST', 'GET'])
def logout():
    global loggedin
    global loggedinEmail
    loggedin = False
    loggedinEmail = ""
    return redirect("/", code=302)

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 