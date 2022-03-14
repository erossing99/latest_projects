import os
import psycopg2

from flask import Flask, render_template, request, g, redirect, url_for, jsonify, send_file, session
from werkzeug.utils import secure_filename
import io

from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = "WE ARE THE LEAKS"

oauth = OAuth(app)

AUTHO0_CLIENT_ID = env['auth0_client_id']
AUTHO0_CLIENT_SECRET = env['auth0_client_secret']
AUTHO0_DOMAIN = env['auth0_domain']

auth0 = oauth.register(
    'auth0',
    client_id=AUTHO0_CLIENT_ID,
    client_secret=AUTHO0_CLIENT_SECRET,
    api_base_url='https://'+AUTHO0_DOMAIN,
    access_token_url='https://'+AUTHO0_DOMAIN+'/oauth/token',
    authorize_url='https://'+AUTHO0_DOMAIN+'/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

####Database Functions

def connect_db():
    return psycopg2.connect(os.environ.get('DATABASE_URL'), sslmode='require')

def get_db():
    if not hasattr(g,'pg_db'):
        g.pg_db = connect_db()
    return g.pg_db

@app.after_request
def close_db(response):
    if hasattr(g, 'db'):
        app.logger.warn("teardown")
        g.pg_db.close()
    return response

###Auth0 Functions

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect(url_for('main'))

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external = True))

#Use this function wrapper to make urls unreachable if client not logged in
def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.route('/logout')
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('main', _external=True), 'client_id': AUTHO0_CLIENT_ID}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))


@app.route('/')
def main():
    return redirect(url_for('post_gallery'))

@app.route('/people')
def people():
    conn = get_db()

    cur = conn.cursor()
    cur.execute("SELECT * FROM person;")
    names = [record[1] for record in cur]
    cur.close()

    return render_template("people.html", names=names)

##Image Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['png', 'jpg', 'jpeg']

@app.route('/image', methods=['POST'])
def upload_post():
    # check if the post request has the file part
    if 'image' not in request.files:
        return redirect(url_for("post_gallery", status="Image Upload Failed: No selected file"))
    file = request.files['image']
    average_rgb = request.form.get('rgb_average')
    rgb_1 = request.form.get('rgb_1')
    rgb_2 = request.form.get('rgb_2')
    rgb_3 = request.form.get('rgb_3')
    metadata = request.form.get('metadata')
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return redirect(url_for("post_gallery", status="Image Upload Failed: No selected file"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        data = file.read()
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO posts (username, filename, data, rgb_1, rgb_2, rgb_3, average_rgb, metadata) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (session["profile"]["name"], filename, data, rgb_1, rgb_2, rgb_3, average_rgb, metadata))
        conn.commit()
        cur.close()
    return redirect(url_for("post_gallery", status="Image Uploaded Succesfully"))

@app.route('/image', methods=['GET'])
def post_gallery():
    status = request.args.get("status", "")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT post_id FROM posts ORDER BY post_id desc limit 12 ;")
    post_ids = [r[0] for r in cur]
    # cur.execute("SELECT COUNT(*) FROM posts ;")
    cur.execute("SELECT rgb_1 FROM posts ORDER BY post_id desc limit 12 ;")
    rgb_1_array = [r[0] for r in cur]
    cur.execute("SELECT rgb_2 FROM posts ORDER BY post_id desc limit 12 ;")
    rgb_2_array = [r[0] for r in cur]
    cur.execute("SELECT rgb_3 FROM posts ORDER BY post_id desc limit 12 ;")
    rgb_3_array = [r[0] for r in cur]
    return render_template("home.html", post_ids = post_ids, rgb_1_array = rgb_1_array, rgb_2_array = rgb_2_array, rgb_3_array = rgb_3_array)

@app.route('/image/<int:post_id>')
def view_post(post_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE post_id=%s", (post_id,))
    post_row = cur.fetchone()
    cur.close()
    stream = io.BytesIO(post_row[3])

    # use special "send_file" function
    return send_file(stream, attachment_filename=post_row[2])


@app.route('/upload')
def upload():
    return render_template("upload.html")

#Temporary route for testing -> a profile button in the header will need to route here IF LOGGED IN
# I believe Kluver showed example where you can have element hidden if user isn't logged in
@app.route('/profile')
def profile():
    if session.get('profile') is None:
        return redirect(url_for('login'))
    else:

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT post_id FROM posts WHERE username = %s ORDER BY post_id desc limit 12 ;",(session['profile']['name'],))
        post_ids = [r[0] for r in cur]
        return render_template("profile.html", post_ids=post_ids)

@app.route('/image', methods=['POST'])
def upload_profile_photo():
    file = request.files['image']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        #data = file.read()
        #conn = get_db()
        #cur = conn.cursor()
        #cur.execute("SELECT * FROM users where username=%s", (username,))
        #post_row = cur.fetchone()
        #cur.close()
        #stream = io.BytesIO(post_row[x]) <--- x will the column that holds the user's profile picture
        #return send_file(stream, attachment_filename=post_row[2])

'''
 This will be changed eventually when the profile picture upload functionality is implemented- Khalid
@app.route('/profilepicture')
def profile_picture(username):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users where username=%s", (username,))
    post_row = cur.fetchone()
    cur.close()
    stream = io.BytesIO(post_row[x]) <--- x will the column that holds the user's profile picture
    return send_file(stream, attachment_filename=post_row[2])
'''

@app.route('/editProfile')
def editProfile():
    return render_template("editProfile.html")

#@app.route('/editUsername')
#def editUsername():
    #return render_template("profile.html")
