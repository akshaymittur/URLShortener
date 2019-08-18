from flask import Flask, request, render_template,redirect
from math import floor
from sqlite3 import OperationalError
import string, sqlite3
try:
    from urllib.parse import urlparse
    str_encode = str.encode
except ImportError:
    print("Error Importing Urllib")
import base64

app = Flask(__name__)
host = 'http://localhost:5000/'



def encode_url(id):
    #URL Shortening Function: to base62
    characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base = len(characters)
    val = id % base
    res = characters[val]
    index = id // base

    while index:
        val = index % base
        index = id // base
        res = characters[int(val)] + res

    return res

def decode_url(encodedurl):
    #URL Decoding Function: to base10
    characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base = len(characters)
    limit = len(encodedurl)
    res = 0
    for i in range(limit):
        res = base * res + characters.find(encodedurl[i])
    
    return res

def check_table():
    #Function to check if table in database is created
    create_table = """
        CREATE TABLE WEBSITE_URLS(
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            URL TEXT NOT NULL
        );
        """
    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
        except OperationalError:
            pass

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        originalUrl = str_encode(request.form.get('url'))
        if urlparse(originalUrl).scheme == '':
            url = 'http://' + originalUrl
        else:
            url = originalUrl

        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            res = cursor.execute(
                'INSERT INTO WEBSITE_URLS (URL) VALUES (?)',
                [base64.urlsafe_b64encode(url)]
                )
            encoded_string = encode_url(res.lastrowid)

        return render_template('home.html', short_url = host + encoded_string)

    return render_template('home.html')

@app.route('/<short_url>')
def redirect_short_url(short_url):
    decoded_url = decode_url(short_url)
    url = host #If no URL is Found

    with sqlite3.connect('urls.db') as conn:
        cursor = conn.cursor()
        res = cursor.execute('SELECT URL FROM WEBSITE_URLS WHERE ID=?', [decoded_url])
        try:
            short = res.fetchone()
            if short is not None:
                url = base64.urlsafe_b64decode(short[0])
        except Exception as err:
            print (err)
    
    return redirect(url)


if __name__ == '__main__':
    #Checks if Table is Created
    check_table()
    app.run(debug=True)