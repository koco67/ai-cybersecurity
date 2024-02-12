from argparse import ArgumentParser


def getStandardArgParser():
    parser = ArgumentParser()
    parser.add_argument("-du", "--dbuser", dest="dbUser", default=None,
                        help="username for MYSQL Database")
    parser.add_argument("-dp", "--dbpassword", dest="dbPassword", default=None,
                        help="password for MySQL Database")
    parser.add_argument("-s", "--savecredentials",
                        action="store_true", dest="saveCredentials", default=False,
                        help="store given credentials on Windows/Linux Keyring")
    parser.add_argument("-d", "--defaultuser",
                        action="store_true", dest="setDefaultUser", default=False,
                        help="set given user as default User (can only be used together with --saveCredentials)")
    return parser
