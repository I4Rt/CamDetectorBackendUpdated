from flask import Flask, request, json
from time import time
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

from flask_cors import CORS, cross_origin
from datetime import timedelta
import os
directory = os.getcwd().replace('\\','/')
app = Flask(__name__, template_folder=f'{directory}/system/templates', static_folder=f'{directory}/system/backend/fileSystem', static_url_path = '')

app.config['TIME'] = time()
app.config['SIZE'] = 1000
app.config['TYPES'] = {1: 'Нет на месте', 2: 'Съемка экрана'}

directory = os.getcwd()

UPLOAD_FOLDER = directory + '/system/backend/fileSystem'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)
cors = CORS(app, supports_credentials=True, resources={r"*": {"origins": "*"}})