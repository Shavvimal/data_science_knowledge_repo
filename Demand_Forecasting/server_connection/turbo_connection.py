from dotenv import load_dotenv
import os
import traceback
import turbodbc
load_dotenv()

server = os.getenv('SERVER_NAME')
database = os.getenv('DATABASE_NAME')
username = os.getenv('UID')
password = os.getenv('PASSWORD')

def connect():
    print('Attempting connection ......')
    try:
        connection = turbodbc.connect(driver="SQL Server",
                      server=server,
                      database=database,
                      uid=username,
                      pwd=password)
    except Exception as exception:
        traceback.print_exc()
        return

    print('Connected')
    return connection