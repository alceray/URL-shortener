from flask import Flask, redirect, render_template, request, url_for
import sqlite3
import string
import requests
from urllib.parse import urlparse

app = Flask(__name__)

BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
host = "http://localhost:5000/"

def encode(id, base = BASE62):
    baselen = len(base)
    encoded_id = ""
    while id:
        encoded_id = base[id % baselen] + encoded_id
        id //= baselen
    return encoded_id

def decode(code, base = BASE62):
    baselen = len(base)
    codelen = len(code)
    id = 0
    for i in range(codelen):
        id += base.find(code[i]) * (baselen ** (codelen - i - 1))
    return id

def valid_url(url):
    try:
        response = requests.get(url)
        return True
    except:
        return False

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        og_url = request.form["url"]
        if urlparse(og_url).scheme == '':
            og_url = 'https://' + og_url
        if not valid_url(og_url):
            return 'ERROR: URL is invalid. <a href="">Try again<a>.'
        conn = sqlite3.connect('urls.sqlite')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS URL_LIST (ID INTEGER PRIMARY
            KEY AUTOINCREMENT, URL TEXT NOT NULL UNIQUE)''')
        cur.execute('INSERT OR IGNORE INTO URL_LIST (URL) VALUES (?)', (og_url,))
        cur.execute("SELECT ID FROM URL_LIST WHERE URL='"+og_url+"'")
        id = cur.fetchone()[0]
        conn.commit()
        conn.close()
        encoded_url = host + encode(id)
        return render_template("shorten.html", short_url = encoded_url)
    return render_template("shorten.html")

@app.route("/<short_url>")
def get_og_url(short_url):
    id = decode(short_url)
    conn = sqlite3.connect('urls.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT URL FROM URL_LIST WHERE ID='+str(id))
    try:
        og_url = cur.fetchone()[0]
    except:
        conn.close()
        return 'ERROR: URL was not found.'
    conn.close()
    return redirect(og_url)

if __name__ == "__main__":
    app.run(debug=True)