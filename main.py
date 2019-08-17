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

class UrlShortener:
    characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    base = len(characters)

    def shortenUrl(self, id):
        
        val = id % base
        res = characters[val]
        index = id // base

        while index:
            val = index % base
            index = id // base
            res = characters[int(val)] + res

        return res

    def decode(self, encodedurl):
        limit = len(encodedurl)
        res = 0
        for i in range(limit):
            res = base * res + characters.find(encodedurl[i])
        
        return res

    def check_table(self):
        create_table = """
            CREATE TABLE WEBSITE_URLS(
                ID INT PRIMARY KEY AUTOINCREMENT,
                URL TEXT NOT NULL
            );
            """
        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(create_table)
            except OperationalError:
                pass

Shortener = UrlShortener()

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        originalUrl = str_encode(request.form.get('url'))
        if urlparse(originalUrl).scheme == '':
            url = 'http://' + originalUrl
        else:
            url = originalUrl

        with sqlite3.connect('urls.db') as conn:
            cursor = conn.cursor
            res = cursor.execute(
                'INSERT INTO WEB_URL (URL) VALUES (?)',
                [base64.urlsafe_b64encode(url)]
                )
            encoded_string = Shortener.shortenUrl(res.lastrowid)

        return render_template('home.html', short_url = host + encoded_string)

    return render_template('home.html')



if __name__ == '__main__':
    check_table()
    app.run()