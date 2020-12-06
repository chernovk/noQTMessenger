import pyodbc
import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


def connection():
    con = pyodbc.connect('DRIVER={Devart ODBC Driver for MySQL};'
                         f'User ID={os.environ["db_username"]};'
                         f'Password={os.environ["db_password"]};'
                         'Server=mymessenger.mysql.database.azure.com;'
                         f'Database={os.environ["database"]};'
                         'Port=3306;')
    return con
