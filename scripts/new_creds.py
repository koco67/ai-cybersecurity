import api_methods
from database import Database
from stdArgParser import getStandardArgParser
import api_methods

parser = getStandardArgParser()
args = parser.parse_args()
# Usage example
db_username = "sql11683464"
db_password = "SfFsKWIcWP"
db_host = "sql11.freemysqlhosting.net"
db_name = "sql11683464"
db_port = 3306

# Create an instance of Database with automatic connection
cursor = Database(db_username, db_password, db_host, db_name, db_port)

def store_credentials(username, password):
    # Hash the password before storing it in the database
    hashed_password = api_methods.hash_password(password)

    # Store the username and hashed password in the MySQL table
    query = "INSERT INTO USERS (username, password_hash) VALUES (%s, %s)"
    cursor.executeSQL(query, (username, hashed_password))




# Disconnect from the database when done
store_credentials("b","b")