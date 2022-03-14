import os
import psycopg2
import json

from flask import Flask, render_template, request, g, jsonify
app = Flask(__name__)

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

@app.route('/')
def consent_page():
    return render_template('consent.html')

@app.route('/survey')
def survey():
    return render_template('survey.html')

@app.route('/decline')
def decline():
    return render_template('decline.html')

@app.route('/thanks', methods=['POST',])
def survey_post():
    #get survey values
    name = request.form.get('name')
    fav_character = request.form.get('fav_character')
    season = request.form.get('radio')
    if "current" in request.form:
        current = request.form.get('current')
    else:
        current = 'not current'
    justification = request.form.get('justification')
    #add them to the database
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO survey (name, fav_character, season, current, justification) values (%s, %s, %s, %s, %s)", (name, fav_character, season, current, justification))
    conn.commit()
    cur.close()
    return render_template("thanks.html")

@app.route("/api/results")
def api_results():
    reverse = request.args.get("reverse", "false")
    conn = get_db()
    cur = conn.cursor()
    if (reverse == "false"):
        cur.execute("SELECT * FROM survey;")
        return jsonify(cur.fetchall())
    else:
        cur.execute("SELECT * FROM survey ORDER BY person_id DESC;")
        return jsonify(cur.fetchall())
