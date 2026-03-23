import hashlib

from app import login
from app.models import User

def auth_user(username, password):
    password = hashlib.md5(password.encode('utf-8')).hexdigest()
    return User.query.filter(
        User.username == username,
        User.password == password,
        User.active == True
    ).first()

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))