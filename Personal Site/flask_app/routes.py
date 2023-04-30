# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
    if 'email' in session:
        return session['email']
    return 'Unknown'

@app.route('/login')
def login():
	return render_template('login.html', user=getUser())

@app.route('/users')
def users():
    return db.query("SELECT * FROM users")

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    if db.authenticate(form_fields['email'], form_fields['password']):
        session['email'] = form_fields['email']
        return json.dumps({'success': 1})
    return json.dumps({'failure': 1})


#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    if db.isOwner(getUser()):
        role = 'owner'
    else:
        role='user'
    return render_template('chat.html', role=role, user=getUser() )

@socketio.on('joined', namespace='/chat')
def joined(message):
    join_room('main')
    if db.isOwner(getUser()):
        emit('status', {'message': getUser() + ' has entered the room.', 'role': 'owner'}, room='main')
    else: 
        emit('status', {'message': getUser() + ' has entered the room.', 'role': 'user' }, room='main')

@socketio.on('leave', namespace='/chat')
def leave():
    if db.isOwner(getUser()):
        emit('status', {'message': getUser() + ' has left the room.', 'role': 'owner'}, room='main')
    else: 
        emit('status', {'message': getUser() + ' has left the room.', 'role': 'user' }, room='main')
    leave_room('main')


@socketio.on('send_message', namespace='/chat')
def sendMessage(message):
    join_room('main')
    emit('status', message, room='main')

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	print(db.query('SELECT * FROM users'))
	return render_template('home.html', user=getUser())

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	return render_template('resume.html', resume_data = resume_data, user=getUser())

@app.route('/projects')
def projects():
	return render_template('projects.html', user=getUser())

@app.route('/piano')
def piano():
	return render_template('piano.html', user=getUser())


@app.route('/processfeedback', methods=['POST'])
def processFeedback():
	db.insertRows(columns=['name', 'email', 'comment'], parameters=[[request.form['name'], request.form['email'], request.form['feedback']]], table="feedback")
	feedbackData = db.query(query="SELECT * FROM feedback")
	return render_template("feedback.html", comments=feedbackData, user=getUser())


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
