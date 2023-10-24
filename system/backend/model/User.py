import flask_login

users = {'admin': {'password': 'password'}}
class User(flask_login.UserMixin):
    pass