import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['boards', 'tasks', 'users', 'user_boards']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        ''' FILL ME IN WITH CODE THAT CREATES YOUR DATABASE TABLES.'''

        #should be in order or creation - this matters if you are using forign keys.
         
        if purge:
            for table in self.tables[::-1]:
                self.query(f"""DROP TABLE IF EXISTS {table}""")
            
        # Execute all SQL queries in the /database/create_tables directory.
        for table in self.tables:
            
            #Create each table using the .sql file in /database/create_tables directory.
            with open(data_path + f"create_tables/{table}.sql") as read_file:
                create_statement = read_file.read()
            self.query(create_statement)

            # Import the initial data
            try:
                params = []
                with open(data_path + f"initial_data/{table}.csv") as read_file:
                    scsv = read_file.read()            
                for row in csv.reader(StringIO(scsv), delimiter=','):
                    params.append(row)
            
                # Insert the data
                cols = params[0]; params = params[1:] 
                self.insertRows(table = table,  columns = cols, parameters = params)
            except:
                print('no initial data')

    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id



#######################################################################################
# BOARD RELATED
#######################################################################################
    def createBoard(self, users = [], boardName='new board'):
        board_id = self.insertRows('boards',['name'], [[boardName]])
        self.insertRows('tasks',['board_id', 'title', 'description', 'state'], [[board_id, 'Task 1', 'TODO', 0],[board_id, 'Task 2', 'TODO', 0]])
        self.insertRows('user_boards', ['board_id', 'user_id'], [[board_id, userId]for userId in users])
    
    def getBoards(self, email):
        user_id = self.query(f"SELECT user_id FROM users WHERE email = '{email}'")[0]['user_id']
        print(user_id)
        boards = self.query(f"""SELECT boards.board_id, boards.name FROM boards, user_boards
             WHERE boards.board_id = user_boards.board_id AND user_boards.user_id = {user_id}""")
        for board in boards:
            board['insights'] = self.getTaskInsights(board['board_id'])
            board['members'] = self.getMembers(board['board_id'])
        print(boards)
        return boards


    def getTaskInsights(self, board_id):
        todo = self.query(f"SELECT COUNT(task_id) as todo FROM tasks WHERE board_id = {board_id} AND state = 0")[0]
        doing = self.query(f"SELECT COUNT(task_id) as doing FROM tasks WHERE board_id = {board_id} AND state = 1")[0]
        complete = self.query(f"SELECT COUNT(task_id) as complete FROM tasks WHERE board_id = {board_id} AND state = 2")[0]
        return {**todo,**doing,**complete}

    def getMembers(self, board_id):
        members = self.query(f"SELECT email FROM users, user_boards WHERE user_boards.board_id = {board_id} AND users.user_id = user_boards.user_id")
        return [member['email'] for member in members]

    def getBoardName(self, board_id):
        return self.query(f"SELECT name FROM boards WHERE board_id = {board_id}")[0]['name']

    def getTasks(self, board_id):
        tasks = self.query(f"SELECT task_id, title, description, state FROM tasks WHERE board_id = {board_id}")
        return tasks

    def updateTask(self, task_id, task_state, task_description, task_title):
        self.query(f"UPDATE tasks SET state = {task_state}, description = '{task_description}', title = '{task_title}' WHERE task_id = {task_id}")
        return task_id

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password'):
        if len(self.query(f"SELECT email FROM users WHERE email = '{email}'")) == 0:
            self.insertRows(columns=['email', 'password'], parameters=[[email, self.onewayEncrypt(password)]], table='users')
            return True
        return False

    def authenticate(self, email='me@email.com', password='password'):
        if len(users := self.query(f"SELECT user_id, email, firstsignin FROM users WHERE email = '{email}' and password = '{self.onewayEncrypt(password)}'")) == 1:
            return True, users[0]['firstsignin'] == 1, users[0]['user_id']
        return False, None, None

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string


    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


