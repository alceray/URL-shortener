from flask import Flask, redirect, render_template, request, url_for
import sqlite3
import string
import requests
import random
from urllib.parse import urlparse

app = Flask(__name__)

BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
max_num = 10**7
all_nums = list(range(max_num))
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

def valid_key(key):
    for letter in key:
        if letter not in BASE62:
            return False
    return True

def unique_rand_num(lst = all_nums, len = max_num):
    i = random.randrange(len)
    lst[i], lst[-1] = lst[-1], lst[i]
    return lst.pop()

@app.route("/", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        og_url = request.form["url"]
        new_url = request.form["key"]
        if urlparse(og_url).scheme == '':
            og_url = 'https://' + og_url
        if not valid_url(og_url):
            return 'ERROR: URL is invalid. <a href="">Try again<a>.'
        if not valid_key(new_url):
            return 'ERROR: URL key contains invalid character(s). <a href="">Try again<a>.'
        if new_url == "":
            new_url = encode(unique_rand_num())
        conn = sqlite3.connect('urls.sqlite')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS URL_LIST (ID TEXT NOT NULL UNIQUE, URL TEXT NOT NULL UNIQUE)''')
        cur.execute('SELECT URL FROM URL_LIST WHERE ID=(?)',(new_url,))
        try:
            cur.fetchone()[0]
            conn.commit()
            conn.close()
            return "ERROR: URL key is already used. <a href="">Try again<a>."
        except:
            cur.execute('INSERT OR IGNORE INTO URL_LIST (ID,URL) VALUES (?,?)',(new_url,og_url))
            cur.execute("SELECT ID FROM URL_LIST WHERE URL=(?)",(og_url,))
            stored_id = cur.fetchone()[0]
            encoded_url = host + stored_id
            conn.commit()
            conn.close()
            return render_template("shorten.html", short_url = encoded_url)
    return render_template("shorten.html")

@app.route("/<short_url>")
def get_og_url(short_url):
    if not valid_key(short_url):
        return 'ERROR: URL was not found.'
    conn = sqlite3.connect('urls.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT URL FROM URL_LIST WHERE ID=(?)',(short_url,))
    try:
        og_url = cur.fetchone()[0]
    except:
        conn.close()
        return 'ERROR: URL was not found.'
    conn.close()
    return redirect(og_url)

if __name__ == "__main__":
    app.run(debug=True)