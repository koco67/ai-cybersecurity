import mysql.connector

class Database:
    def __init__(self, username, password, host, database, port):
        self.username = username
        self.password = password
        self.host = host
        self.database = database
        self.port = port
        self.connection = None
        self.cursor = None

        # Automatically connect during initialization
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                user=self.username,
                password=self.password,
                host=self.host,
                database=self.database,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Disconnected from the database.")

    def executeSQL(self, query, parameters=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, parameters)
            self.connection.commit()
            print("Query executed successfully.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
    
    def getScalarResult(self, query, parameters=None):
        try:
            cursor = self.connection.cursor()
            if parameters is None:
                cursor.execute(query)
            else:
                cursor.execute(query, parameters)

            return cursor.fetchone()[0]
        except Exception as e:
            print("An error getting scalar result. Query: {}. Error message: {}".format(query, e))
            return None
        finally:
            cursor.close()
        
# Usage example
db_username = "sql11683464"
db_password = "SfFsKWIcWP"
db_host = "sql11.freemysqlhosting.net"
db_name = "sql11683464"
db_port = 3306

