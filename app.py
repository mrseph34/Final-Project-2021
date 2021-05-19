from flask import Flask, render_template, json, jsonify, request, current_app as app
from datetime import date
import os
import requests
import sqlite3 as sql

app = Flask(__name__, static_folder="static")

con = sql.connect("data.db")
cur = con.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS "users" ("username"  TEXT, "password"  TEXT)')

print(cur.fetchall())

cur.close

@app.route('/')
def index():
 
    return render_template('index.html')

if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0') 