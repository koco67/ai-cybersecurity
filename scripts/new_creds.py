import datetime
import api_methods
from database import Database
from stdArgParser import getStandardArgParser
import api_methods

parser = getStandardArgParser()
args = parser.parse_args()
# Usage example
db_username = "sql11686549"
db_password = "e9JNxGrzxE"
db_host = "sql11.freemysqlhosting.net"
db_name = "sql11686549"
db_port = 3306

# Create an instance of Database with automatic connection
cursor = Database(db_username, db_password, db_host, db_name, db_port)

current_date = datetime.date.today().strftime("%Y-%m-%d")

def store_credentials(username, password, email, registered):
    # Hash the password before storing it in the database
    hashed_password = api_methods.hash_password(password)

    # Store the username and hashed password in the MySQL table
    query = "INSERT INTO USERS (username, password_hash, email, registrierung_zeitpunkt) VALUES (%s, %s, %s, %s)"
    cursor.executeSQL(query, (username, hashed_password, email, registered))




# Disconnect from the database when done
store_credentials("admin","admin", "admin@gmail.com", current_date)
