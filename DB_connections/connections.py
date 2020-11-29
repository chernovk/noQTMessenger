import pyodbc

username = "Ravenom"
password = "Ravenom01"
database = "messenger"


def connection():
    con = pyodbc.connect(
        "DRIVER={Devart ODBC Driver for MySQL};"
        f"User ID={username};"
        f"Password={password};"
        "Server=localhost;"
        f"Database={database};"
        "Port=3306;"
        "String Types=Unicode"
    )
    return con
