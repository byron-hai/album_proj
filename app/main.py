# -*- coding: utf-8 -*-
import os
import yaml
import logging
from flask import Flask, session, flash, request, redirect,\
                  render_template, url_for, abort
from werkzeug.utils import secure_filename
from boto_s3 import S3

fmt = '%(levelname)-6s %(message)s'
logging.basicConfig(level='INFO', format=fmt)
logger = logging.getLogger(__file__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "album")
ALLOWED_EXTENSIONS = {'.png', '.jpg'}

app = Flask(__name__)
app.secret_key = 'random string'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if os.path.exists('config.yml'):
    with open('config.yml', 'r') as ymfile:
       cfg = yaml.load(ymfile)
else:
    logger.error("Config file not found")
def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return redirect(url_for('home', user=username))

    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
   return render_template('signup.html') 


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        if session['username'] == 'admin' and session['password'] == 'admin':
            return redirect(url_for('home', user=session['username']))
        else:
            flash('Username or Password error! Try again.')
            return redirect(request.url)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/home/<user>')
def home(user):
    if user is None:
        abort(404)

    photos = 'get all photos by user'
    return render_template('home.html', user=user, photos=photos)


@app.route('/home/<user>/upload', methods=['GET', 'POST'])
def upload_file(user):
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(url_for('home', user=session['username']))

        img_file = request.files['image']

        if img_file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        elif not allowed_file(img_file.filename):
            flash('Wrong format. Not in '+ ', '.join(list(ALLOWED_EXTENSIONS)))
            return redirect(url_for('home', user=user))
        else:
            local_img_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(img_file.filename))
            img_file.save(local_img_path)

            if os.path.exists(local_img_path):
                try:
                    session = S3(aws_key=cfg['aws_key'], aws_secret=cfg['aws_secret'], region=cfg['region'])
                    url = session.upload_file_to_s3(local_img_path,
                                                    cfg['bucket'],
                                                    secure_filename(img_file.filename))
                    if url:
                        logger.info(url)
                        ''' Store url to dynamodb '''
                        flash('Uploading finished.')
                        return redirect(url_for('home', user=user))
                    else:
                        logger.error("URL not returned")
                except Exception as err:
                    logger.error(str(err))
                
                return redirect(url_for('home', user=user))
            else:
                logger.error('Save to local folder failed')
                flash('Upload failed. Try again')
                return redirect(url_for('home', user=user))
    return redirect(request.url)
    
if __name__ == '__main__':
    app.run(debug=True)
