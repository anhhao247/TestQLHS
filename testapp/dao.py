from testapp.models import User
from testapp import app, db
import hashlib
from werkzeug.security import check_password_hash


def check_login(username, password, role=None):
    if username and password:
        password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
        u = User.query.filter(User.username.__eq__(username.strip()),
                              User.password.__eq__(password))
        if role:
            u = u.filter(User.user_role.__eq__(role))
        return u.first()

def get_user_by_id(user_id):
    return User.query.get(user_id)