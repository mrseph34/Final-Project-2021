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

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("fname" TEXT, "lname" TEXT, "email" TEXT, "password" TEXT, "profilePic" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_posts" ("post" TEXT, "title" TEXT, "date" TEXT, "name" TEXT, "description" TEXT, "likes" TEXT, "likesAmount" INTEGER, "comments" TEXT, "email" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_comments" ("id", "name", "comment", "date","email")')
con.commit()
cur.close()

app.secret_key = "secret key"
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER
app.config['POSTS_FOLDER'] = POSTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

loggedin = False
loggedinEmail = ""
full_name = ""
change = ""
defPic = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxEHBhERBxASFRISFRcWFhMYFRcWFhgVFRYWFhgbFxYYHSggGB0lHRUTLTEhJSkrLi4uFx8zODMuOigtMCsBCgoKBQUFDgUFDisZExkrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrKysrK//AABEIAOEA4QMBIgACEQEDEQH/xAAbAAEAAgMBAQAAAAAAAAAAAAAABQYBAwQCB//EAD0QAQABAgMDCAcGBQUBAAAAAAABAgMEBREhMVEGEkFhcYGh0RMUIkKRscEjMjNScuE1YoKS8FOissLiJf/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwD7GAAAAAAAAAADFUxTGtU6RxBkcF7OLFnfciZ/l9rxjY5auUVqJ9miufhH1BMiFp5R25+9RX4T9XTZzqxdn7/N/VEx47gSI80Vxcp1tzExxidYegAAAAAAAAAAAAAAAAAAAABiZ0jarGc5vOJmaMNOlHTPTV+wO/Mc+pszNOE0qq/N7seav4nF3MVVrfqmerojsjc0gAAAANli/Xh69bFU0z1T8+Kdy/lBzpinHRp/PG7vjo7leAX6mqKqYmmdYndLKo5TmlWBr0r1m3O+OHXHktlu5F23FVudYmNYkHoAAAAAAAAAAAAAAAAGnF34wuGqrq92Ne2eiPjoCG5R5hp9jZn9c/KnzV9m5XNy5NVc6zM6zPXLAAAAAAAAACY5PZh6C96K7Ps1Ts6qvKUOAv448pxXrmBpqq+9Gyrtjz2T3uwAAAAAAAAAAAAAABCcqL/Nw9FEe9Os9lP7z4JtV+U9euPpjhRHjM/sCIAAAAAAAAAAABOclr+l6uiemOdHbGyfnHwWNT8hr5ma2+vWPjTK4AAAAAAAAAAAAAAAKpykj/6f9NP1WtWuVNvTFUVcadP7Z/8AQIUAAAAAAAAAAAHZk0a5pa/V9JXNUuTtvn5pTP5Yqnw0+q2gAAAAAAAAAAAAAAIvlFh/TZfzqd9E6926f86koxVTFdMxVGsTGkx1SCgjozDCzgsXVRVujdPGmd3+dTnAAAAAAAAAB7w9mcRepotb6p0gFg5L4fm2a7lXvTzY7I3+PyTjVhrMYaxTRb3Uxo2gAAAAAAAAAAAAAAAAj84y/wBew/sffp+7PHqlUaqZoqmK40mNkwvyMzbKYxsc61pFzj0VdU+YKmPd+zVh7k03omJjol4AAAAABmiiblcRREzM7ojbIMLRkOW+q2+ffj26o3fljzl5yfJvV5ivFaTX0U74p85TIAAAAAAAAAAAAAAAAAAA811RRTrXMRHGZ0hH4jO7FndVNU8KY18Z2A68VhKMXb0xFMTw4x2T0ILF8naqZ1wlUVR+Wdk/HdPg9XuUkz+BbiOuqdfCHHczy/XuqiOymPrqDlv4K5Y/Gt1R16bPjGxzuurMr1W+7X3Tp8miu9Vc/EqqntmZBrbrOFuX5+xoqnsidPi80XqqPuVTHZMw6KMzv0brtffOvzB24Tk/cuTriZiiOG+ryhO4LAW8FT9hTt6ap2zPerlvPb9H3qqau2mPpo7bPKT/AF7ffTP0nzBYBH4fObF/3+bPCrZ47vF3xOsaxuBkAAAAAAAAAAAAAAEdmma04GNI9qv8vDrqB2371OHt869VERxn/NqCxvKGZnTBU/1VfSnzQ+KxVeLuc6/VrPhHZHQ0g2YjEV4mrW/VNXbPyjoawAAAAAAAAAbsNi7mFn7CuY6uj4bmkBYcFyhirZjadP5o3d8eSct3Iu0RVamJid0xthQnRgsbXgrmtidnTTO6e2AXccWW5lRj6PY2VRvp6e2OMO0AAAAAAAAAHFmuOjAYbX3p2Ux18eyAc+dZr6nTzLP4k/7Y49qrVVTXVM1TrM75Llc3K5quTrMzrM9bAAAAAAAAAAAAAAAAAPVq5Nm5FVqZiY3TC25TmUY+1pVsrjfHHrjqVB7w96rD3ortTpMAvg58Bi6cbhort98cJ6YdAAAAAAAMVTFNOtW6N8qZmeMnHYuavdjZTHCP3TnKTF+hw0W6N9e/9Mec/VWAAAAAAAAAAAAAAAAAAAAASGSY71PF+3PsV7KurhK3qAtuQ4v1rAxFf3qPZns6J+HyBJAAAAA483xHq2XV1RvmObHbVsBVs0xPreOrqjdrpT2Rsjz73KwyAAAAAAAAAAAAAAAAAAAAAkchxPq+YRE7q/Znv3ePzRxE6TsBfxpwd/1nCUVx70RPf0+OrcAAAgOVN/Zbtx11T8o/7J9T89vemzOvTdTpT8N/jqDgAAAAAAAAAAAAAAAAAAAAAAABZuTF7n4Oqifcq8Ktvz1TKq8mr3o8w5s7q6ZjvjbHylagAAea6uZRM1bojX4KHcr9JcmqrfMzPx2rjnN30WWXJ4xp/dMR9VNAAAAAAAAAAAAAAAAAAAAAAAABuwN30GMoq4VR8NdvhqvL5+vOCu+nwdFXGmJ79NoN4AIvlJ/DJ/VT9VUAAAAAAAAAAAAAAAAAAAAAAAAABcck/hVrsn/lLADvAB//2Q=="


@app.route('/')
def index():
    global loggedin
    if loggedin:
        return redirect("/home", code=302)
    return render_template('index.html')

@app.route('/settings')
def settings():
    global loggedin
    global loggedinEmail
    global full_name
    global change
    changed = change
    change = ""
    
    return render_template('settings.html', full_name = full_name, match = False, ematch = False, change=changed)

@app.route('/home')
def home():
    global loggedinEmail
    profilePic = ""

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT * from users WHERE email='"+loggedinEmail+"'")
    pic = cur.fetchall()
    for row in pic:
        profilePic = row[4]
    

    cur.close()

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

    return render_template('home.html', posts = posts, comments=comments, replies="replies", name=full_name, email=loggedinEmail, profilePic = profilePic)

@app.route('/home/post')
def homePost():
    global loggedin
    global loggedinEmail
    global full_name
    email = loggedinEmail

    if loggedin == False:
        print("NOT LOGGED IN")
        return redirect("/", code=302)

    return render_template('posts.html', type=type)

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
    imgname = img.filename
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

    cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email) VALUES((?),(?),(?),(?),(?),(?),(?),(?),(?))", (imgname, title, date, full_name, description, "[]", 0, "[]", email))
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
        
    
    return redirect("/home", code=302)

@app.route('/change_pic',methods = ['POST', 'GET'])
def profilePic():
    global loggedin
    global loggedinEmail
    global full_name
    global change
    img = request.files['prof']
    imgname = img.filename
    if img.filename != "":
        print(img.filename)
        filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['PROFILE_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("UPDATE users SET profilePic = '"+imgname+"' WHERE email='"+loggedinEmail+"'")

    con.commit()
    cur.close()
    con.close()

    change = "PROFILE PIC CHANGED SUCCESSFULLY!"

    return redirect('/settings', code=302) 

@app.route('/register',methods = ['POST', 'GET'])
def register():
    global loggedin
    global loggedinEmail
    global full_name
    global defPic
     
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
        cur.execute("INSERT INTO users(fname, lname, email, password, profilePic) VALUES((?),(?),(?),(?),(?))", (fname, lname, email, password,defPic))
        cur.execute('CREATE TABLE' + insert  + '("post" TEXT, "name" TEXT)')

        loggedin = True
        loggedinEmail = email
        con.commit()

    cur.close()


    return redirect("/home", code=302)

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
    
    return redirect("/home", code=302)


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

    

    date = datetime.datetime.now()

    cur.execute("INSERT INTO all_comments(id, name, comment, date, email) VALUES((?),(?),(?),(?),(?))", (id, full_name, comment, date, loggedinEmail))
    con.commit()

    cur.close()

    return "success", 200

@app.route('/change_password', methods = ['POST', 'GET'])
def change_pass():
    global loggedin
    global loggedinEmail
    global full_name
    
    
    old_pass = request.form.get('old_pass')
    new_pass = request.form.get('new_pass')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT password FROM users WHERE email='"+loggedinEmail+"'")
    curent_password = cur.fetchall()
    curent_password = curent_password[0][0]
    print(curent_password)
    
    con.commit()
    cur.close()

    if(old_pass == curent_password):
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("UPDATE users SET password='"+new_pass+"' WHERE email='"+loggedinEmail+"'")
        con.commit()
        cur.close()
        global change
        change = "PASSWORD CHANGED SUCCESSFULLY!"
        return redirect("/settings", code = 302)
    else:
        print('Not a match')
        match = True
        con.commit()
        cur.close()
        return render_template('settings.html', full_name = full_name, exists = match, ematch = False)
        
@app.route('/change_email', methods = ['POST', 'GET'])
def change_email():


    global loggedin
    global loggedinEmail
    global full_name

    new_email = request.form.get('new_email')
    
    

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    

    cur.execute('SELECT email FROM users')

    emails = cur.fetchall()

    huh = "EMAIL DO NOT EXIST"

    exists = False

    for row in emails:
        if row[0].upper() == new_email.upper():
            huh = "EMAIL EXISTS"
            exists = True

    if huh == "EMAIL DO NOT EXIST":
        cur.execute("UPDATE users SET email='"+new_email+"' WHERE email='"+loggedinEmail+"'")
        loggedinEmail = new_email
        exists = False
        con.commit()
        cur.close()
        global change
        change = "EMAIL CHANGED SUCCESSFULLY!"
        return redirect("/settings", code = 302)
    else:
        return render_template('settings.html', full_name = full_name, match = False, ematch = exists)

@app.route('/change_name', methods = ['POST', 'GET'])
def change_name():
    global loggedin
    global loggedinEmail
    global full_name

    
    
    

    fname = request.form.get('fname')
    lname = request.form.get('lname')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET fname='"+fname+"' WHERE email='"+loggedinEmail+"'")
    cur.execute("UPDATE users SET lname='"+lname+"' WHERE email='"+loggedinEmail+"'")

    full_name = fname + " " + lname
    con.commit()
    cur.close()
    global change
    change = "NAME CHANGED SUCCESSFULLY!"
    return redirect("/settings", code = 302)
    
        

@app.route('/logout',methods = ['POST', 'GET'])
def logout():
    global loggedin
    global loggedinEmail
    loggedin = False
    loggedinEmail = ""
    return redirect("/", code=302)


if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 