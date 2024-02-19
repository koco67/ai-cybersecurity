# tests/test_integration.py

import os
import sys
import unittest
from flask import Flask
from flask_testing import TestCase
import argparse

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.main import app

class IntegrationTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_login_with_wrong_credentials(self):
        response = self.client.post('/', data=dict(
            username='wrong_username',
            password='wrong_password'
        ), follow_redirects=True)

        # Check if the response HTML contains the error message
        self.assertIn(b'Username or password is incorrect', response.data)

    def test_login_with_correct_credentials(self):
        response = self.client.post('/', data=dict(
            username='user',
            password='a'
        ), follow_redirects=True)

        # Check if the response redirects to the main page
        self.assertEqual(response.status_code, 200)  
        self.assertTrue(b'main' in response.data)  

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-du", "--dbuser", help="Database user")
    parser.add_argument("-dp", "--dbpassword", help="Database password")
    parser.add_argument("unittest_args", nargs='*')  # Add this line
    args = parser.parse_args()

    # Set database credentials if provided
    os.environ['DB_USER'] = args.dbuser
    os.environ['DB_PASSWORD'] = args.dbpassword

    # Pass the remaining arguments to unittest
    sys.argv[1:] = args.unittest_args

    # Run the tests
    unittest.main()


# Unfortunately the integration tests dont run because of some import errors that could be fixed on time
# Following changes need to be made to the import in status and imports in main in order for the integration tests to pass
#status
#import scripts.logging_to_file as log statt import logging_to_file as log
#main
#from scripts.ai_model import AIModel statt from ai_model import AIModel
#from .database import Database 
#from .stdArgParser import getStandardArgParser
#from .status import Status
#import scripts.api_methods as api_methods
#run tests command with database username and password
#ai-cybersecurity\scripts> python tests/test_integration.py -du sql11683464 -dp SfFsKWIcWP

