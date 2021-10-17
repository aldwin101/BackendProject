from flask import Flask

app = Flask(__name__)

import mypackage.users
import mypackage.login