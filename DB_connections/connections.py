import pyodbc


username = "Ravenom@mymessenger"
password = "!ko393390"
database = "messenger"


def connection():
    con = pyodbc.connect(
        "DRIVER={Devart ODBC Driver for MySQL};"
        f"User ID={username};"
        f"Password={password};"
        "Server=mymessenger.mysql.database.azure.com;"
        f"Database={database};"
        "Port=3306;"
    )
    return con
