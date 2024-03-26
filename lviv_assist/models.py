from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer
from lviv_assist import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self):
        print(app.secret_key)
        s = Serializer(app.config['SECRET_KEY'])
        t = s.dumps({'user_id': self.id})
        print(s.loads(t), t)
        return t

    @staticmethod
    def verify_reset_token(token):
        print(app.secret_key, token)
        s = Serializer(app.secret_key)
        try:
            print(token)
            user_id = s.loads(token)['user_id']
        except Exception as exUseMe:
            print(exUseMe, type(exUseMe))
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.name}', '{self.surname}', '{self.email}', '{self.image_file})"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_from = db.Column(db.String(20), nullable=False)
    surname_from = db.Column(db.String(20), nullable=False)
    email_from = db.Column(db.String(120), unique=True, nullable=False)
    name_to = db.Column(db.String(20), nullable=False)
    surname_to = db.Column(db.String(20), nullable=False)
    email_to = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"User('{self.hashtag}', '{self.date_posted}')"
    