import csv
import datetime
import io
import json
import os
from flask import Flask, Response, request, jsonify, redirect, send_file, send_from_directory, session, url_for, render_template, flash
from database import Database
from stdArgParser import getStandardArgParser
from status import Status
import api_methods
import hashlib
import pandas as pd
from ai_model import AIModel

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'
parser = getStandardArgParser()
args = parser.parse_args()


ai_model = AIModel()

db_host = "sql11.freemysqlhosting.net"
db_name = "sql11686549"
db_port = 3306

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'csv'}
model_trained = False  # Flag to track the training status

cursor = Database(args.dbUser, args.dbPassword, db_host, db_name, db_port)

status = Status()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload-train", methods=["GET", "POST"])
def upload_train():
    global model_trained  # Use a global variable to track the training status

    if request.method == 'POST':
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'train_data.csv')
            file.save(file_path)

            train_data = pd.read_csv(file_path)

            # Train the model using the uploaded train data
            ai_model.train_model(train_data)

            model_trained = True # Use a global variable to track the training status


            flash('Train data uploaded and model trained successfully!', 'success')
        else:
            flash('Invalid file format. Please upload a valid CSV file.', 'error')


    return render_template('train.html')


@app.route("/upload-test", methods=["GET", "POST"])
def upload_test():
    global model_trained

    if request.method == 'POST':
        file = request.files['file']

        if not model_trained:
            flash('Error: Model has not yet been trained. Please train the model first.', 'error')
            return render_template('test.html')

        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_data.csv')
            file.save(file_path)

            test_data = pd.read_csv(file_path)

            # Get predictions and result file path
            result_file_path = ai_model.predict(test_data)

            flash('Test data uploaded and predictions made successfully!', 'success')

            return send_file(result_file_path, as_attachment=True)

    return render_template('test.html')

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Login page
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if api_methods.check_credentials(username, password, cursor):
            session['username'] = username
            if username == 'admin':
                return redirect(url_for('admin_main_page'))
            else:
                return redirect(url_for('main_page'))
        else:
            status.setStatus(401, "INCORRECT_LOGIN")
    return render_template('login.html')


@app.route("/main", methods=["GET"])
def main_page():
    if 'username' not in session:
        status.setStatus(401, "INCORRECT_LOGIN")
        return render_template('login.html')
    return render_template('main_page.html')

@app.route("/admin-main", methods=["GET"])
def admin_main_page():
    if 'username' not in session:
        status.setStatus(401, "INCORRECT_LOGIN")
        return render_template('login.html')
    return render_template('admin_main_page.html')

@app.route('/add-user', methods=["GET", "POST"])
def add_user():
    if 'username' not in session or session['username'] != 'admin':
        # If not logged in or not admin, redirect to login page
        return redirect(url_for('login'))

    if request.method == "POST":
        # Get the user input from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Assuming 'registered' is the current date/time
        registered = datetime.date.today().strftime("%Y-%m-%d")
        
        result = api_methods.store_credentials(username, password, email, registered, cursor)

        if result == True:
            flash('User added successfully!', 'success')
            # Redirect to the admin main page after adding the user
            return redirect(url_for('admin_main_page'))
        elif result == False:
            flash('Error: Username already exists. Choose a different username.', 'error')

        # Redirect to the admin main page after adding the user
        return redirect(url_for('admin_main_page'))

    return render_template('add_user.html')  # Render the add-user template


@app.route('/sign-out', methods=['POST'])
def sign_out():

    session.pop('username', None)
    return render_template('login.html')

@app.route('/example-page')
def example_page():
    return render_template('example_page.html')

@app.route('/change-password', methods=['GET'])
def change_password_page():
    if 'username' not in session:
        status.setStatus(401, "INCORRECT_LOGIN")
        return render_template('login.html')
    return render_template('change_password.html')

@app.route('/change-password', methods=['POST'])
def change_password():
    if 'username' not in session:
        status.setStatus(401, "INCORRECT_LOGIN")
        return render_template('login.html')
    
    # Get the old and new passwords from the form
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    if len(new_password) <= 7:
        flash('New password must be at least 8 characters long.', 'error')
        return render_template('main_page.html')
    
    # Check if the current password is correct
    if api_methods.check_credentials(session.get('username'), current_password, cursor):
        # Update the password in the database
        query = "UPDATE USERS SET password_hash = %s WHERE username = %s"
        cursor.executeSQL(query, (api_methods.hash_password(new_password), session.get('username')))

        flash('Password changed successfully!', 'success')
    else:
        flash('Incorrect current password. Password not changed.', 'error')

    return render_template('main_page.html')

@app.route('/download-training-example')
def download_training():
    new_data = [
        {"duration": 0, "protocol_type": "tcp", "service": "ftp_data", "flag": "SF", "src_bytes": 491, "dst_bytes": 0, "land": 0, "wrong_fragment": 0, "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 0, "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0, "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0, "count": 2, "srv_count": 2, "serror_rate": 0.17, "srv_serror_rate": 0.03, "rerror_rate": 0.17, "srv_rerror_rate": 0, "same_srv_rate": 0, "diff_srv_rate": 0.05, "srv_diff_host_rate": 0, "dst_host_count": 150, "dst_host_srv_count": 25, "dst_host_same_srv_rate": 0.17, "dst_host_diff_srv_rate": 0.03, "dst_host_same_src_port_rate": 0.17, "dst_host_srv_diff_host_rate": 0, "dst_host_serror_rate": 0.05, "dst_host_srv_serror_rate": 0, "dst_host_rerror_rate": 0, "dst_host_srv_rerror_rate": 0, "class": "normal"},
        {"duration": 0, "protocol_type": "udp", "service": "other", "flag": "SF", "src_bytes": 146, "dst_bytes": 0, "land": 0, "wrong_fragment": 0, "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 0, "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0, "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0, "count": 13, "srv_count": 1, "serror_rate": 0, "srv_serror_rate": 0.08, "rerror_rate": 0, "srv_rerror_rate": 0, "same_srv_rate": 0, "diff_srv_rate": 0, "srv_diff_host_rate": 0.15, "dst_host_count": 255, "dst_host_srv_count": 1, "dst_host_same_srv_rate": 0.6, "dst_host_diff_srv_rate": 0.88, "dst_host_same_src_port_rate": 0, "dst_host_srv_diff_host_rate": 0, "dst_host_serror_rate": 0, "dst_host_srv_serror_rate": 0, "dst_host_rerror_rate": 0, "dst_host_srv_rerror_rate": 0, "class": "normal"},
        {"duration": 0, "protocol_type": "tcp", "service": "private", "flag": "S0", "src_bytes": 0, "dst_bytes": 0, "land": 0, "wrong_fragment": 0, "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 0, "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0, "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0, "count": 123, "srv_count": 6, "serror_rate": 0.1, "srv_serror_rate": 0.05, "rerror_rate": 0, "srv_rerror_rate": 0, "same_srv_rate": 0, "diff_srv_rate": 0, "srv_diff_host_rate": 0.05, "dst_host_count": 255, "dst_host_srv_count": 26, "dst_host_same_srv_rate": 0.1, "dst_host_diff_srv_rate": 0.05, "dst_host_same_src_port_rate": 0, "dst_host_srv_diff_host_rate": 0, "dst_host_serror_rate": 0, "dst_host_srv_serror_rate": 0, "dst_host_rerror_rate": 1, "dst_host_srv_rerror_rate": 1, "class": "anomaly"}
    ]

    csv_content = "duration,protocol_type,service,flag,src_bytes,dst_bytes,land,wrong_fragment,urgent,hot,num_failed_logins,logged_in,num_compromised,root_shell,su_attempted,num_root,num_file_creations,num_shells,num_access_files,num_outbound_cmds,is_host_login,is_guest_login,count,srv_count,serror_rate,srv_serror_rate,rerror_rate,srv_rerror_rate,same_srv_rate,diff_srv_rate,srv_diff_host_rate,dst_host_count,dst_host_srv_count,dst_host_same_srv_rate,dst_host_diff_srv_rate,dst_host_same_src_port_rate,dst_host_srv_diff_host_rate,dst_host_serror_rate,dst_host_srv_serror_rate,dst_host_rerror_rate,dst_host_srv_rerror_rate,class\n"
    for row in new_data:
        csv_content += ','.join(map(str, row.values())) + '\n'

    response = Response(csv_content, content_type='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=training_example.csv"
    return response

@app.route('/download-testing-example')
def download_testing():
    new_data = [
        {"duration": 0, "protocol_type": "tcp", "service": "private", "flag": "REJ", "src_bytes": 0, "dst_bytes": 0, "land": 0, "wrong_fragment": 0, "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 0, "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0, "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0, "count": 229, "srv_count": 10, "serror_rate": 0, "srv_serror_rate": 0.04, "rerror_rate": 0.06, "srv_rerror_rate": 0, "same_srv_rate": 0.06, "diff_srv_rate": 0, "srv_diff_host_rate": 0, "dst_host_count": 255, "dst_host_srv_count": 10, "dst_host_same_srv_rate": 0.04, "dst_host_diff_srv_rate": 0.06, "dst_host_same_src_port_rate": 0, "dst_host_srv_diff_host_rate": 0, "dst_host_serror_rate": 0, "dst_host_srv_serror_rate": 0, "dst_host_rerror_rate": 1, "dst_host_srv_rerror_rate": 1},
        {"duration": 0, "protocol_type": "tcp", "service": "private", "flag": "REJ", "src_bytes": 0, "dst_bytes": 0, "land": 0, "wrong_fragment": 0, "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 0, "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0, "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0, "count": 136, "srv_count": 1, "serror_rate": 0, "srv_serror_rate": 0.01, "rerror_rate": 0.06, "srv_rerror_rate": 0, "same_srv_rate": 0.06, "diff_srv_rate": 0, "srv_diff_host_rate": 0, "dst_host_count": 255, "dst_host_srv_count": 1, "dst_host_same_srv_rate": 0.06, "dst_host_diff_srv_rate": 0, "dst_host_same_src_port_rate": 0, "dst_host_srv_diff_host_rate": 0, "dst_host_serror_rate": 0, "dst_host_srv_serror_rate": 0, "dst_host_rerror_rate": 1, "dst_host_srv_rerror_rate": 1},
        {"duration": 2, "protocol_type": "tcp", "service": "ftp_data", "flag": "SF", "src_bytes": 12983, "dst_bytes": 0, "land": 0, "wrong_fragment": 0, "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 0, "num_compromised": 0, "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0, "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0, "is_guest_login": 0, "count": 1, "srv_count": 1, "serror_rate": 0, "srv_serror_rate": 0.61, "rerror_rate": 0.04, "srv_rerror_rate": 0.61, "same_srv_rate": 0.02, "diff_srv_rate": 0, "srv_diff_host_rate": 0, "dst_host_count": 134, "dst_host_srv_count": 86, "dst_host_same_srv_rate": 0.61, "dst_host_diff_srv_rate": 0.04, "dst_host_same_src_port_rate": 0.61, "dst_host_srv_diff_host_rate": 0.02, "dst_host_serror_rate": 0, "dst_host_srv_serror_rate": 0, "dst_host_rerror_rate": 0, "dst_host_srv_rerror_rate": 0}
    ]

    csv_content = "duration,protocol_type,service,flag,src_bytes,dst_bytes,land,wrong_fragment,urgent,hot,num_failed_logins,logged_in,num_compromised,root_shell,su_attempted,num_root,num_file_creations,num_shells,num_access_files,num_outbound_cmds,is_host_login,is_guest_login,count,srv_count,serror_rate,srv_serror_rate,rerror_rate,srv_rerror_rate,same_srv_rate,diff_srv_rate,srv_diff_host_rate,dst_host_count,dst_host_srv_count,dst_host_same_srv_rate,dst_host_diff_srv_rate,dst_host_same_src_port_rate,dst_host_srv_diff_host_rate,dst_host_serror_rate,dst_host_srv_serror_rate,dst_host_rerror_rate,dst_host_srv_rerror_rate\n"
    for row in new_data:
        csv_content += ','.join(map(str, row.values())) + '\n'

    response = Response(csv_content, content_type='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=testing_example.csv"
    return response

if __name__ == '__main__':
    
    parser = getStandardArgParser()
    args = parser.parse_args()
    app.run(debug=True)


