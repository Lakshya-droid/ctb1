from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

login = LoginManager()
db = SQLAlchemy()

class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(1000))
    bintpk = db.Column(db.String(1000))
    bintsk = db.Column(db.String(1000))
    binpk = db.Column(db.String(1000))
    binsk = db.Column(db.String(1000))
    otp=db.Column(db.String(8))
    strategy=db.Column(db.String(65533))
    start=db.Column(db.String(1000))
    verified=db.Column(db.String(100))
    wid_list=db.Column(db.String(1000))
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)


@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))