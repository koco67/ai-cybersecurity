import datetime
from flask import redirect, render_template, session, url_for
import hashlib
import os


def hash_password(password):
    # Hash the password using a secure hashing algorithm (e.g., SHA-256)
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashed_password

def store_credentials(username, password, email, registered, cursor):
    # Hash the password before storing it in the database
    hashed_password = hash_password(password)

    # Check if the username already exists in the database
    query = "SELECT username FROM USERS WHERE username = %s"
    used_username = cursor.getScalarResult(query, (username,))

    if used_username:
        return False  # Username already exists
    else:
        # Store the username and hashed password in the MySQL table
        query = "INSERT INTO USERS (username, password_hash, email, registrierung_zeitpunkt) VALUES (%s, %s, %s, %s)"
        cursor.executeSQL(query, (username, hashed_password, email, registered))
        return True  # User added successfully
    
def check_credentials(username, password, cursor):
    # Hash the provided password for comparison with the stored hashed password
    hashed_password_attempt = hash_password(password)

    # Fetch the hashed password from the database for the given username
    query = "SELECT password_hash FROM USERS WHERE username = %s"
    stored_password_hash = cursor.getScalarResult(query, (username,))

    if stored_password_hash and hashed_password_attempt == stored_password_hash:
        return True
    return False

    
# unused method to check if training/test csv file is correct
def check_dates(data):
    date_fields = ['example'] #name columns with date as expected values
    invalid_dates = []

    for entry in data:
        for field in date_fields:
            if field not in entry:
                continue

            date_value = entry[field]
            if not is_valid_date(date_value):
                invalid_dates.append(f"{field} in entry {entry}")

    if invalid_dates:
        message = f"Invalid dates in fields: {', '.join(invalid_dates)}"
        return False, message
    else:
        return True, None
    
# unfinished method to display the predictions on screen
def generate_html_response(response_messages):
    # Dynamic content for the table
    table_content = ""
    for message in response_messages:
        table_content += f"<tr><td>{message['user']}</td><td>{message['prediction']}</td></tr>"

    return render_template('response.html', table_content=table_content)

# unfinished method, a try to check if all uploaded data is correct before allowing it to get uploaded
# this method would be used to check is the date is valid and in the correct format
def is_valid_date(date_string, date_format="%d.%m.%y"):
    try:
        # Attempt to parse the date using the specified format
        datetime.datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False