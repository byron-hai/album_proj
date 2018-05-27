# -*- coding: utf-8 -*-
import os
import yaml
import logging
from datetime import datetime
from flask import Flask, session, flash, request, redirect,\
                  render_template, url_for, abort
from werkzeug.utils import secure_filename
from boto_s3 import S3
from dynamodb import DynamoDB

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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        db = DynamoDB(region=cfg['region'])
        user_table = cfg['db_tbl']['user']

        if not db._isTable_exists(user_table):
            db.create_table(table_name=user_table,
                            attr_dict={'hash_name': "username"})

        user_info = {'username': username.strip(),
                     'password': password.strip(),
                     'email': email.strip()}

        db.insert_item(user_table, user_info)
        return redirect(url_for('login'))

    return render_template('signup.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']

        db = DynamoDB(region=cfg['region'])
        user_table = cfg['db_tbl']['user']

        if not db._isTable_exists(user_table):
            db.create_table(table_name=user_table,
                            attr_dict={'hash_name': "username"})

        try:
            user = db.get_item(user_table, {'username': session['username']})
            if user and user['password'] == session['password']:
                return redirect(url_for('home', user=session['username']))
        except:
            flash('Username or Password does not exist')
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

    try:
        photo_table = cfg['db_tbl']['album']
        photos = DynamoDB(region=cfg['region']).scan_item(photo_table, 'owner', user)
    
        return render_template('home.html', user=user, photos=photos)
    except Exception as err:
        logger.info(err) 
        return render_template('home.html', user=user, photos='')

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
                logger.debug('Image saved. %s', local_img_path)

                try:
                    filename = secure_filename(img_file.filename)
                    session = S3(aws_key=cfg['aws_key'], aws_secret=cfg['aws_secret'], region=cfg['region'])
                    url = session.upload_file_to_s3(local_img_path, cfg['bucket'], filename)

                    db = DynamoDB(region=cfg['region'])
                    photo_table = cfg['db_tbl']['album']

                    if not db._isTable_exists(photo_table):
                        db.create_table(table_name=photo_table,
                                        attr_dict={'hash_name':'owner', 'range_name': 'group'})
                    if url:
                        db.insert_item(photo_table, {'owner': user,
                                                     'group': cfg['group']['pub'],
                                                     'filename': filename,
                                                     'url': url,
                                                     'upload_date': datetime.now().date().strftime('%Y-%m-%d'),
                                                     })

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
