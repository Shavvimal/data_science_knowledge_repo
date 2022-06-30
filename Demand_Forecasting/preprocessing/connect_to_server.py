import pyodbc 
from dotenv import load_dotenv
import os

load_dotenv()

server = os.getenv('SERVER_NAME')
database = os.getenv('DATABASE_NAME')
username = os.getenv('UID')
password = os.getenv('PASSWORD')

def connect():
    print('Attempting connection ......')
    try:
        conn = pyodbc.connect('driver={SQL Server};server=%s;database=%s;uid=%s;pwd=%s;Trusted_Connection=no;' % ( server, database, username, password ) )
    except: 
        print('Connection was unsuccessful.')
        return

    print('Connected')
    return conn
