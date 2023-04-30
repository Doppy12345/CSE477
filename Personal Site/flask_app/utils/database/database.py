import mysql.connector
import glob
from pathlib import Path
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
        self.tables         = ['institutions', 'positions', 'experiences', 'skills','feedback', 'users']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'averysaltysailortookalongwalkoffashortbridge',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : '7pK_fnSKIjZKuv_Gwc--sZEMKn2zc8VvD6zS96XcNHE='}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT CURDATE()", parameters = None):

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

    def about(self, nested=False):    
        query = """select concat(col.table_schema, '.', col.table_name) as 'table',
                          col.column_name                               as column_name,
                          col.column_key                                as is_key,
                          col.column_comment                            as column_comment,
                          kcu.referenced_column_name                    as fk_column_name,
                          kcu.referenced_table_name                     as fk_table_name
                    from information_schema.columns col
                    join information_schema.tables tab on col.table_schema = tab.table_schema and col.table_name = tab.table_name
                    left join information_schema.key_column_usage kcu on col.table_schema = kcu.table_schema
                                                                     and col.table_name = kcu.table_name
                                                                     and col.column_name = kcu.column_name
                                                                     and kcu.referenced_table_schema is not null
                    where col.table_schema not in('information_schema','sys', 'mysql', 'performance_schema')
                                              and tab.table_type = 'BASE TABLE'
                    order by col.table_schema, col.table_name, col.ordinal_position;"""
        results = self.query(query)
        if nested == False:
            return results

        table_info = {}
        for row in results:
            table_info[row['table']] = {} if table_info.get(row['table']) is None else table_info[row['table']]
            table_info[row['table']][row['column_name']] = {} if table_info.get(row['table']).get(row['column_name']) is None else table_info[row['table']][row['column_name']]
            table_info[row['table']][row['column_name']]['column_comment']     = row['column_comment']
            table_info[row['table']][row['column_name']]['fk_column_name']     = row['fk_column_name']
            table_info[row['table']][row['column_name']]['fk_table_name']      = row['fk_table_name']
            table_info[row['table']][row['column_name']]['is_key']             = row['is_key']
            table_info[row['table']][row['column_name']]['table']              = row['table']
        return table_info



    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )
        
        cur = cnx.cursor()

        if purge:
            with open(data_path + "/reset_tables/resetTables.sql") as resetTables:
                statements = resetTables.readlines()
                for statement in statements:
                    cur.execute(statement)
                    

        tables = list(Path(data_path + "/create_tables/").glob('*'))
        tables.sort()
        
        for table in tables:
            tableSql = table.read_text()
            cur.execute(tableSql)
        cnx.commit()
        cur.close()
        cnx.close()

    def prepopulateTables(self,filename):
            
            tableName = filename[:-4]
            
            with open("flask_app/database/initial_data/" + filename) as file:
                file_data = csv.reader(file, delimiter=',')
                columns = None
                rows = []
                for line in file_data:
                    if columns is None:
                        columns = line
                        continue
                    rows.append(line)
                self.insertRows(columns,rows,table=tableName)



    def insertRows(self, columns, parameters, table=None):
        if table is None:
            return
        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )

        cur = cnx.cursor(dictionary=True)
        query = f"""INSERT INTO {table} ({', '.join(columns)})
        VALUES ({', '.join('%s' for c in columns)})
        """

        for parameterSet in parameters:

            for i, parameter in enumerate(parameterSet):
                if parameter == "NULL":
                    parameterSet[i] = None

            cur.execute(query, tuple(parameterSet))

        cnx.commit()
        cur.close()
        cnx.close()

    def getSkills(self, exp_id):
        return self.query(query=f"""SELECT * FROM skills 
        INNER JOIN exp_skills ON exp_skills.exp_id = {exp_id} AND skills.skill_id = exp_skills.skill_id
          """)

    def getExperiences(self, position_id):
        return self.query(f"""SELECT * FROM experiences 
        WHERE position_id = {position_id} 
          """)    

    def getPositions(self, inst_id):
        return self.query(f"""SELECT * FROM positions
        WHERE inst_id = {inst_id} 
          """) 
          
    def getInstitutions(self):
        return self.query(f"SELECT * FROM institutions")  

    def getResumeData(self):
        resumeData = self.getInstitutions()

        
        for institution in resumeData:
            institution['positions'] = self.getPositions(institution['inst_id'])
            for position in institution['positions']:
                position['experiences'] = self.getExperiences(position['position_id'])
                for experience in position['experiences']:
                    experience['skills'] = self.getSkills(experience['exp_id'])

        return resumeData

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        if len(self.query(f"SELECT email FROM users WHERE email = '{email}'")) == 0:
            self.insertRows(columns=['email', 'password', 'role'], parameters=[[email, self.onewayEncrypt(password), role]], table='users')
            return {'success': 1}
        return {'failure': 1}

    def authenticate(self, email='me@email.com', password='password'):
        if len(self.query(f"SELECT email FROM users WHERE email = '{email}' and password = '{self.onewayEncrypt(password)}'")) == 1:
            return True
        return False

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

    def isOwner(self, email):
        rows = self.query(f"SELECT role FROM users where email = '{email}'")
        if len(rows) != 1:
            return False
        if rows[0]['role'] == 'owner':
            return True
        return False


