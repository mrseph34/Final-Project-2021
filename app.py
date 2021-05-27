from re import M
from flask import Flask, redirect, flash, render_template, json, jsonify, request, current_app as app
from datetime import date, datetime
import os
import flask_login
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import requests
import sqlite3 as sql
import urllib.request
from werkzeug.utils import secure_filename
import datetime
from flask_mail import Mail, Message
import string, random

PROFILE_FOLDER = 'static/profile/'
POSTS_FOLDER = 'static/posts/'

today = date.today()

app = Flask(__name__, static_folder="static")

mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'hootsservice@gmail.com'
app.config['MAIL_PASSWORD'] = 'hootytoot'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

def resetPassword(email,tempPass):
    msg = Message('Hello', sender = 'hootsservice@gmail.com', recipients = [email])
    msg.body = "Hello fellow Hooter, your password has been set to the following temporary password please login and change as you please. __"+tempPass+"__"
    mail.send(msg)

login_manager = LoginManager(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self,email):
         self.email = email
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.email

@login_manager.user_loader
def load_user(user_id):
   conn = sql.connect('./static/data/data.db')
   curs = conn.cursor()
   curs.execute("SELECT * from users where email = (?)",[user_id])
   lu = curs.fetchone()
   if lu is None:
      return None
   else:
      return User(lu[2])

con = sql.connect("./static/data/data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("fname" TEXT, "lname" TEXT, "email" TEXT, "password" TEXT, "profilePic" TEXT, "bio" TEXT, "security question" TEXT, "security answer" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "followers" ("follower" TEXT,"following" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "friendships" ("party1" TEXT,"party2" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_posts" ("post" TEXT, "title" TEXT, "date" TEXT, "name" TEXT, "description" TEXT, "likes" TEXT, "likesAmount" INTEGER, "comments" TEXT, "email" TEXT, "profilePic" TEXT, "day" TEXT, "banner" TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS "all_comments" ("id", "name", "comment", "date","email")')
cur.execute('CREATE TABLE IF NOT EXISTS "all_messages" ("rowID" INTEGER PRIMARY KEY, "email1", "email2", "name1", "name2", "message", "date")')

con.commit()
cur.close()

app.secret_key = "secret key"
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER
app.config['POSTS_FOLDER'] = POSTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

full_name = ""
change = ""
defPic = "data:image/jpeg;base64,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"

@app.route('/')
def index():
    
    if current_user.get_id() != None:

        return  redirect("/home", code=302)
    
    return render_template('index.html')


@app.route('/friends/<friend>')
def friend(friend):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()
    
    if friend != email:
        cur.execute('SELECT * FROM friendships WHERE party1="'+email+'" OR party2="'+email+'"')
        friends = cur.fetchall()

        friends_already = False

        for thing in friends:
            if thing[0] == email:
                if thing[1] == friend:
                    friends_already = True
                    
            if thing[1] == email:
                if thing[0] == friend:
                    friends_already = True
                
        if friends_already == False:
            cur.execute("INSERT INTO friendships(party1, party2) VALUES((?),(?))", (email,friend))
            con.commit()
            con.close()
            
    
    

    
    return redirect('/friends')

@app.route('/friends')
def l():
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    email = current_user.get_id()

    cur.execute('SELECT * FROM friendships WHERE party1="'+email+'" OR party2="'+email+'"')
    friends_list = cur.fetchall()
    con.commit()
    con.close()
    list = []
    names = []

    for friends in friends_list:
        friend = [getName(friends[0]),getName(friends[1])]
        if friends[0] == email:
            list.append(friend[1])
        else:
            list.append(friend[0])
        
    return render_template('friends.html', list = list, email = email)

@app.route('/profile')
@login_required
def profile(person):
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    email = current_user.get_id()

    follows = "Follow+"
    cur.execute('SELECT following FROM followers WHERE following="'+email+'"')
    followings = cur.fetchall()
    for follower in followings:
        if follower[0] == email:
            follows = "Follow(-)"

    pic_sql = 'SELECT profilePic FROM users WHERE email=?'
    cur.execute(pic_sql, (email,))
    pic = cur.fetchall()
    pic = pic[0][0]

    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (email,))
    fname = cur.fetchall()
    fname = fname[0][0]

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (email,))
    lname = cur.fetchall()
    lname = lname[0][0]

    cur.execute('SELECT * FROM all_posts WHERE email="'+email +'"')
    posts = cur.fetchall()
    post_num = len(posts)

    cur.execute('SELECT * FROM followers WHERE following="'+email +'"')
    follow = cur.fetchall()
    followersAmt = len(follow)
    
    name = fname + " " + lname
    
    return render_template('profile.html', email=email, pic = pic, name = name, post_num = post_num, followers=followersAmt, follows=follows)
@app.route('/messages')
@login_required
def messages2():

    email = current_user.get_id()
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    msg = ""

    cur.execute("SELECT * FROM all_messages")
    bob = cur.fetchall()
    
    messages = []
    for row in bob:
        message = [row[1],row[2],row[3],row[4],row[5],row[6]]
        messages.append(message)
 
    cur.close() 
    con.close()

    return render_template('messages.html', messages = messages)

    


@app.route('/messages/<reciever>')
def messages(reciever):

    email = current_user.get_id()
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    msg = ""

    fname_sql = 'SELECT fname FROM users WHERE email=?'
    cur.execute(fname_sql, (reciever,))
    fname = cur.fetchall()
    fname = fname[0][0]

    lname_sql = 'SELECT lname FROM users WHERE email=?'
    cur.execute(lname_sql, (reciever,))
    lname = cur.fetchall()
    lname = lname[0][0]

    reciever_name = fname + " " + lname

    cur.execute("INSERT INTO all_messages(email1, email2, name1, name2, message, date) VALUES((?),(?),(?),(?),(?),(?))", (email,reciever,getName(None),reciever_name,msg,datetime.datetime.now()))
    con.commit()

    #cur.execute("INSERT INTO all_messages(email1, email2, message, date) VALUES((?),(?),(?),(?))", (email,reciever,msg,datetime.datetime.now()))

    return render_template('messages.html', reciever = reciever, name = reciever_name, messages = "bob")

@app.route('/settings')
@login_required
def settings():
    
    full_name = getName(None)
    global change
    changed = change
    change = ""
    
    return render_template('settings.html', full_name = full_name, match = False, ematch = False, change=changed)

@app.route('/ForgotPassword')
def forgotPassword():
    if current_user.get_id() != None:

        return  redirect("/home", code=302)
        
    return render_template("change.html",info="Enter your email address associated with the account:")

@app.route('/ForgotPassword/<email>')
def forgotPassword2(email):
    if current_user.get_id() != None:

        return  redirect("/home", code=302)

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("SELECT email FROM users")

    emails = cur.fetchall()

    for row in emails:
        if row[0].upper() == email.upper():
            tempPass = ""
            for i in range(12):
                r  = random.choice(string.ascii_letters)
                tempPass = tempPass+r
            con = sql.connect("./static/data/data.db")
            cur = con.cursor()
            cur.execute("UPDATE users SET password='"+tempPass+"' WHERE email='"+email+"'")
            con.commit()
            cur.close()
            resetPassword(email,tempPass)
            return render_template("change.html", info = "A change password email has been sent to "+email)
    
    cur.close()
    con.close()
    return render_template("change.html", info = "Email does not exists please enter the correct email address associated with the account:")

@app.route('/home')
@login_required
def home():

    full_name = getName(None)
    
    profilePic = []

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users')

    all = cur.fetchall()

    users = []

    for row in all:
        users.append(row[4])

    cur.close()
    con.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
       
    cur.execute("SELECT profilePic,email from users")
    pic = cur.fetchall()
    for row in pic:
        profilePic.append(row)
 
    

    cur.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]]
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

    return render_template('home.html', users=users, posts = posts, comments=comments, replies="replies", name=full_name, email=current_user.get_id(), profilePic = profilePic)

@app.route('/home/post')
@login_required
def homePost():
    
    
    full_name = getName(None)
    email = current_user.get_id()

    

    return render_template('posts.html', type=type)

@app.route('/post', methods=['GET', 'POST'])
def post():
    
    
    full_name = getName(None)
    email = current_user.get_id()

    


    img = request.files['img']
    imgname = img.filename
    if img.filename != "":
       
        filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['POSTS_FOLDER'], filename))
        
        flash('Image successfully uploaded and displayed below')


    title = request.form.get("title", False)
    description = request.form.get("description", False)
    day = today.strftime("%B %d, %Y")
    date = datetime.datetime.now()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT profilePic FROM users WHERE email='"+current_user.get_id()+"'")
    profPic = cur.fetchall()[0][0]
    con.commit()
    cur.close()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email, profilePic, day) VALUES((?),(?),(?),(?),(?),(?),(?),(?),(?),(?),(?))", (imgname, title, date, full_name, description, "[]", 0, "[]", email, profPic, day))
    #cur.execute("INSERT INTO " + email.upper() + "(post, name) VALUES((?),(?))", (post, full_name))
    #cur.execute("INSERT INTO all_posts(post, title, date, name, description, likes, likesAmount, comments, email) VALUES((?),(?))", (post, full_name))
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]]
        posts.append(post)

    con.commit()
    con.close()
        
    
    return redirect("/home", code=302)

@app.route('/change_pic',methods = ['POST', 'GET'])
@login_required
def profilePic():
    
    
    full_name = getName(None)
    email = current_user.get_id()
    global change
    img = request.files['prof']
    imgname = img.filename
    if img.filename != "":
       
        filename = secure_filename(img.filename)
        img.save(os.path.join(app.config['PROFILE_FOLDER'], filename))
       
        flash('Image successfully uploaded and displayed below')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute("UPDATE users SET profilePic = '"+imgname+"' WHERE email='"+current_user.get_id()+"'")
    cur.execute("UPDATE all_posts SET profilePic='"+imgname+"' Where email='"+current_user.get_id()+"'")     

    con.commit()
    cur.close()
    con.close()

    change = "PROFILE PIC CHANGED SUCCESSFULLY!"

    return redirect('/settings', code=302) 

@app.route('/register',methods = ['POST', 'GET'])
def register():
    global defPic
     
    

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
        

        con.commit()

    cur.close()
    con.close()

    return redirect("/home", code=302)

@app.route('/login',methods = ['POST', 'GET'])
def login():

    name = ""
    email = request.form.get('email', False)
    password = request.form.get('password', False)

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    cur.execute('SELECT * FROM users')

    all = cur.fetchall()
    
    exists = False

    for row in all:
        if email!=False:
            if row[2].upper() == email.upper():
                exists = True
                if row[3] == password:
                    name = row[0]
                    
                    
                    Us = load_user(email)
                    login_user(Us, remember = email)
                    
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
    con.close()
    
    return redirect("/home", code=302)


@app.route('/like/<id>',methods = ['POST', 'GET'])
@login_required
def like(id):
    
    
    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("SELECT * from all_posts")
    rows = cur.fetchall()
    posts = []
    for row in rows:
        post = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]]
        posts.append(post)
    cur.close()
    for post in posts:
        if id == post[2]:
            if ","+current_user.get_id() not in post[5]:
                con = sql.connect("./static/data/data.db")
                cur = con.cursor()
                cur.execute("UPDATE all_posts SET likesAmount=likesAmount+1 WHERE date='"+post[2]+"'")
                cur.execute("UPDATE all_posts SET likes=trim(',"+current_user.get_id()+"') WHERE date='"+post[2]+"'")
                con.commit()

                cur.close()
                con.close()
                return "successDrop"
                
            con = sql.connect("./static/data/data.db")
            cur = con.cursor()
            cur.execute("UPDATE all_posts SET likesAmount=likesAmount-1 WHERE date='"+post[2]+"'")
            cur.execute("UPDATE all_posts SET likes=likes+',"+current_user.get_id()+"' WHERE date='"+post[2]+"'")
            con.commit()

            con.close()
            cur.close()
    return "success", 200

@app.route('/follow/<following>',methods = ['POST', 'GET'])
@login_required
def follow(following):

    email = current_user.get_id()

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    follows = "Follow+"
    cur.execute('SELECT following FROM followers WHERE following="'+following+'"')
    followings = cur.fetchall()
    for follower in followings:
        if follower[0] == email:
            follows = "Follow(-)"

    if follows == "Follow+":
        cur.execute("INSERT INTO followers(follower,following) VALUES((?),(?))", (email,following))
        con.commit()
    if follows == "Follow(-)":
        cur.execute("DELETE FROM followers WHERE follower='"+email+"' AND following='"+following+"'")
        con.commit()

    cur.close()
    con.close()

    return "success", 200

@app.route('/comment/<comment>/<id>',methods = ['POST', 'GET'])
@login_required
def comments(comment,id):
    
    full_name = getName(None)

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()

    date = datetime.datetime.now()

    cur.execute("INSERT INTO all_comments(id, name, comment, date, email) VALUES((?),(?),(?),(?),(?))", (id, full_name, comment, date, current_user.get_id()))
    con.commit()

    cur.close()
    con.close()

    return "success", 200

@app.route('/change_password', methods = ['POST', 'GET'])
@login_required
def change_pass():
    
    
    full_name = getName(None)
    
    
    old_pass = request.form.get('old_pass')
    new_pass = request.form.get('new_pass')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    
    cur.execute("SELECT password FROM users WHERE email='"+current_user.get_id()+"'")
    curent_password = cur.fetchall()
    curent_password = curent_password[0][0]
    print(curent_password)
    
    con.commit()
    cur.close()

    if(old_pass == curent_password):
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("UPDATE users SET password='"+new_pass+"' WHERE email='"+current_user.get_id()+"'")
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
@login_required
def change_email():


    
    
    full_name = getName(None)

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
        cur.execute("UPDATE users SET email='"+new_email+"' WHERE email='"+current_user.get_id()+"'")
        Us = load_user(new_email)
        login_user(Us, remember = new_email)
        exists = False
        con.commit()
        cur.close()
        global change
        change = "EMAIL CHANGED SUCCESSFULLY!"
        return redirect("/settings", code = 302)
    else:
        return render_template('settings.html', full_name = full_name, match = False, ematch = exists)

@app.route('/change_name', methods = ['POST', 'GET'])
@login_required
def change_name():
      
    full_name = getName(None)

    fname = request.form.get('fname')
    lname = request.form.get('lname')

    con = sql.connect("./static/data/data.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET fname='"+fname+"' WHERE email='"+current_user.get_id()+"'")
    cur.execute("UPDATE users SET lname='"+lname+"' WHERE email='"+current_user.get_id()+"'")
    cur.execute("UPDATE all_posts SET name='"+fname+" "+lname+"' Where email='"+current_user.get_id()+"'")  
    cur.execute("UPDATE all_comments SET name='"+fname+" "+lname+"' Where email='"+current_user.get_id()+"'")  

    full_name = fname + " " + lname
    con.commit()
    cur.close()
    global change
    change = "NAME CHANGED SUCCESSFULLY!"
    return redirect("/settings", code = 302)
    
def getName(email):

    if email == None:
        email = current_user.get_id()
        
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT fname FROM users WHERE email='"+email+"'")
        fname = cur.fetchall()[0][0]
        con.commit()
        cur.close()

        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT lname FROM users WHERE email='"+email+"'")
        lname = cur.fetchall()[0][0]


        full_name = fname + " " + lname
        con.commit()
        cur.close()
    else:
        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT fname FROM users WHERE email='"+email+"'")
        fname = cur.fetchall()[0][0]
        con.commit()
        cur.close()

        con = sql.connect("./static/data/data.db")
        cur = con.cursor()
        cur.execute("SELECT lname FROM users WHERE email='"+email+"'")
        lname = cur.fetchall()[0][0]


        full_name = fname + " " + lname
        con.commit()
        cur.close()
    
    return full_name

@app.route('/logout',methods = ['POST', 'GET'])
@login_required
def logout():
    
    logout_user()

    return redirect("/", code=302)


if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 