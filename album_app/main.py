# -*- coding: utf-8 -*-
import os
from flask import Flask, session, flash, request, redirect,\
                  render_template, url_for, abort
from werkzeug.utils import secure_filename

BASE_DIR = os.getcwd()
UPLOAD_FOLDER = os.path.join(BASE_DIR, "album")
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

app = Flask(__name__)
app.secret_key = 'random string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return redirect(url_for('home', user=username))

    return "You are not logged in <br><a href='/login'></b>" + \
           "click here to log in</b></a>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        if session['username'] == 'admin' and session['password'] == 'admin':
            flash('You were loged in')
            return redirect(url_for('home', user=session['username']))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/home/<user>')
def home(user):
    if user is None:
        abort(404)

    photos = 'get all photos by user'
    return render_template('home.html', user=user, photos=photos)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        img_file = request.files['image']

        if img_file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        elif not allowed_file(img_file.filename):
            flash('Wrong format. Not in '+ ', '.join(list(ALLOWED_EXTENSIONS)))
            return redirect(url_for('home', user=session['username']))
        else:
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(img_file.filename)))
            return redirect(url_for('home', user=session['username']))

    return redirect(request.url)
    

if __name__ == '__main__':
    app.run(debug=True)
