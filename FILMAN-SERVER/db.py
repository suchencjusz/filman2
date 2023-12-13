import os
import mysql.connector

# MYSQL_HOST = "127.0.0.1"
# MYSQL_USER = "root"
# MYSQL_PASSWORD = ""
# MYSQL_DATABASE = "filmweb_test"

MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "filmweb_test2")

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()
