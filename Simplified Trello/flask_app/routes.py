# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
from time import sleep
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
	return session['email'] if 'email' in session else 'Unknown'

@app.route('/login')
def login():
	return render_template('login.html', action='Login', user=getUser())

@app.route('/signup')
def signup():
    return render_template('signup.html', action='Sign Up', user=getUser())

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/')

@app.route('/users')
def users():
    return json.dumps({
        'users': db.query('SELECT * from users'), 
        'user_boards': db.query('SELECT * FROM user_boards'),
        'boards': db.query('SELECT * FROM boards'),
        'tasks': db.query('SELECT * FROM tasks') })

@app.route('/processlogin', methods = ["POST","GET"])
def processlogin():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    auth, isNew, userId = db.authenticate(form_fields['email'], form_fields['password'])
    if auth:
        session['email'] = form_fields['email']
        session['isNew'] = isNew
        db.query(f"UPDATE users SET firstsignin = FALSE WHERE user_id = {userId}")
        return json.dumps({'success': 1})
    return json.dumps({'failure': 1})

@app.route('/createUser', methods = ["POST", "GET"])
def createUser():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    if db.createUser(email=form_fields['email'], password=form_fields['password']):
        return json.dumps({'success': 1})
    return json.dumps({'failure' : 1})
#######################################################################################
# CHATROOM RELATED
#######################################################################################

@socketio.on('joinChat', namespace='/chat')
def joined(message, room):
    join_room(room)
    emit('transfer', {'message': getUser() + ' has entered the room.', 'user': getUser()}, to=room)

@socketio.on('sendMessage', namespace='/chat')
def sendMessage(messageData, room):
    join_room(room)
    emit('status', messageData,  to=room)

@socketio.on('leaveChat', namespace="/chat")
def leave(room):
    emit('transfer', {'message': getUser() + ' has left the room.', 'user': getUser()}, to=room)
    

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
@login_required
def home():

    return render_template('home.html', user=getUser(), myBoards=db.getBoards(session['email']), isNew=session['isNew'])

@app.route('/createBoard', methods=['POST'])
@login_required
def createBoard():
    emails = request.form['email'].split(',')
    emails = [f"'{email.strip()}'" for email in emails]
    emails.append(f"'{getUser()}'")
    emails = ','.join(emails)
    users = db.query(f"SELECT user_id FROM users WHERE email IN ({emails})")
    users = [user['user_id'] for user in users]
    db.createBoard(users, request.form['name'])
    session['isNew'] = False
    return redirect('/home')


@app.route('/updateTask', methods=['POST'])
@login_required
def updateTask():
    form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
    db.updateTask(form_fields['task_id'], form_fields['state'], form_fields['description'], form_fields['title'])
    return json.dumps({'success': 1})

@app.route('/board/<boardId>/tasks', methods=['GET', 'POST'])
@login_required
def boardTasks(boardId):
    if request.method == 'GET':
        tasks = db.getTasks(boardId)
        return json.dumps(tasks)
    if request.method == 'POST':
        form_fields = dict((key, request.form.getlist(key)[0]) for key in list(request.form.keys()))
        if db.insertRows('tasks', ['board_id', 'title', 'description', 'state'], [[boardId, form_fields['title'], form_fields['description'], form_fields['state']]]) <= 0:
            return json.dumps({'failure': 1})
        return json.dumps({'success': 1})

@app.route("/board/<boardId>")
@login_required
def board(boardId):
    return render_template('board.html', board_id=boardId , user=getUser(), boardName=db.getBoardName(boardId), tasks=db.getTasks(boardId))

@socketio.on('boardUpdate', namespace="/chat")
def boardUpdate(room):
    emit('task_update', to=room)

@socketio.on('lockTask', namespace='/chat')
def lockTask(taskData, room):
    emit('task_edit', taskData, to=room)


@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r
