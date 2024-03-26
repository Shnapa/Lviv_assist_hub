"""
This application provides assistance for users in Lviv. It allows users to register, login, update 
their profiles, search for employees based on hashtags, post descriptions of services they offer, 
view profiles of other users, and leave comments on those profiles.
"""
import os
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, request, flash,request, Flask, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired
from lviv_assist import app, db, bcrypt, mail
from lviv_assist.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from lviv_assist.models import User
from lviv_assist.users_database import ShowEmployees, GetHashtags, Filter
from lviv_assist.comments import GetComments, AddComments
from flask_mail import Message, Mail

class CommentForm(FlaskForm):
    """
    A form class for submitting comments.
    """
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LvivAssist:
    """
    Main class for Lviv Assist application.
    """

    def __init__(self, app):
        """
        Initialize Lviv Assist application.
        """
        self.app = app
        self.db = db
        self.bcrypt = bcrypt

    def run(self):
        """
        Run the Lviv Assist application.
        """
        self.app.run(debug=True)

class Homepage:
    """
    Class for handling the home page route.
    """
    @app.route("/")
    @staticmethod
    def home():
        """
        Renders the home page template.
        """
        return render_template("home.html")

class UserAuthentication:
    """
    Class for user authentication related operations.
    """

    @staticmethod
    @app.route('/logout', methods=['GET','POST'])
    def logout():
        """
        Logs out the current user.
        """
        logout_user()
        return redirect(url_for('home'))

    @staticmethod
    @app.route('/login', methods=['GET','POST'])
    def login():
        """
        Logs in the user if credentials are valid.
        """
        if current_user.is_authenticated:
            return redirect(url_for('account'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('account'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        return render_template('login.html', title='Log in', form=form)



class UserRegistration:
    """
    Class for user registration related operations.
    """

    @staticmethod
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        Registers a new user.
        """
        if current_user.is_authenticated:
            return redirect(url_for('post'))
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = User(name=form.name.data, \
surname=form.surname.data, email=form.email.data, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', title='Register', form=form)

class Picture:
    """
    Utility class for managing user profile pictures.
    """
    @staticmethod
    def save_picture(form_picture):
        """
        Save user profile picture.
        """
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

        output_size = (125, 125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_fn

class UserProfile:
    """
    Class for managing user profiles.
    """
    @staticmethod
    @app.route("/account", methods=['GET', 'POST'])
    @login_required
    def account():
        """
        Renders the account page with options to update profile.
        """
        form = UpdateAccountForm()
        if form.validate_on_submit():
            picture_file = Picture.save_picture(form.picture.data)
            current_user.image_file = picture_file
            current_user.name = form.name.data
            current_user.surname = form.surname.data
            current_user.email = form.email.data
            db.session.commit()
            return redirect(url_for('account'))
        form.name.data = current_user.name
        form.surname.data = current_user.surname
        form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('account.html', title='Account',
                        image_file=image_file, form=form)

class LvivAssistApp(LvivAssist, Picture):
    """
    Main Lviv Assist application class.
    """

    def __init__(self, app):
        """
        Initialize Lviv Assist application class.
        """
        super().__init__(app)
        self.registration_form = RegistrationForm
        self.login_form = LoginForm
        self.update_account_form = UpdateAccountForm
        self.comment_form = CommentForm

    def home(self):
        """
        Home page route.
        """
        @self.app.route("/")
        def home():
            return render_template("home.html")

    def register(self):
        """
        User registration route.
        """
        @self.app.route('/register', methods=['GET', 'POST'])
        def register():
            if current_user.is_authenticated:
                return redirect(url_for('post'))
            form = self.registration_form()
            if form.validate_on_submit():
                hashed_password = self.bcrypt.generate_password_hash\
(form.password.data).decode('utf-8')
                user = User(name=form.name.data, surname=form.surname.data, \
email=form.email.data, password=hashed_password)
                self.db.session.add(user)
                self.db.session.commit()
                flash('Your account has been created! You are now able to log in', 'success')
                return redirect(url_for('login'))
            return render_template('register.html', title='Register', form=form)

class Search:
    """
    Class for handling search operations.
    """
    @staticmethod
    @app.route('/employee_search')
    def employee_search():
        """
        Renders the employee search page.
        """
        return render_template("index_search.html", hashtags=list(set(GetHashtags.get_hashtags())))

    @staticmethod
    @app.route("/get_companies")
    def get_companies():
        """
        Retrieves companies based on hashtags.
        """
        hashtag = request.args.get('hashtag')
        return ShowEmployees.show_employees(hashtag)

class Posts:
    """
    Class for handling posts.
    """
    @staticmethod
    @app.route('/post')
    def post():
        """
        Renders the post page.
        """
        hashtags = GetHashtags.get_hashtags()
        return render_template("post.html", hashtags=hashtags)

    @staticmethod
    @app.route('/add_post', methods=['POST'])
    @login_required
    def add_post():
        """
        Adds a new post.
        """
        description = request.form['description']
        price = request.form['price']
        hashtag = request.form['hashtag']
        name = current_user.name
        surname = current_user.surname
        email = current_user.email
        Filter.add_hashtag_profile(name, surname, email, description, \
price, hashtag[0].upper() + hashtag[1:])
        flash('Your post has been created!', 'success')
        return redirect(url_for('post'))

    @staticmethod
    @app.route('/success')
    def success():
        """
        Renders the success page after adding a post.
        """
        hashtags = GetHashtags.get_hashtags()
        return render_template("success.html", hashtags=hashtags)

class Profile:
    """
    Class for handling user profiles.
    """

    @staticmethod
    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        """
        Renders the profile page with comments and user details.
        """
        email = request.args.get('email')
        description = request.args.get('description')
        employee = ShowEmployees.get_employee(email=email, description=description)
        image_file = User.query.filter_by(email=email).first().image_file
        print("Image file:", image_file)
        email_to = employee.email
        if current_user.is_authenticated and request.method == 'POST':
            name_from = current_user.name
            name_to = request.form.get('name_to')
            surname_to = request.form.get('surname_to')
            body = request.form.get('body')
            AddComments.add_comment(name_from, name_to, surname_to, email_to, description, body)
        comments=GetComments.get_comments(name_from=None,
                            email_to=email_to,
                            description=description)
        return render_template('profile.html', employee=employee, \
comments=comments, image_file=os.path.join('static/profile_pics', image_file))


class ResettingPassword:
    @staticmethod
    def send_reset_email(user):
        token = user.get_reset_token()
        msg = Message('Password Reste Request',
                    sender='lvivassisthub@gmail.com',
                    recipients=[user.email])
        msg.body = f"""To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)} 

    If you didn't make this request then  simply ignore this email and no changes will be made 
    """
        mail.send(msg)

    @staticmethod
    @app.route("/reset_password", methods=['GET', 'POST'])
    def reset_request():
        if current_user.is_authenticated:
            return redirect(url_for('account'))
        form = RequestResetForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email = form.email.data).first()
            ResettingPassword.send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('login'))
        return render_template('reset_request.html', title='Reset Password', form=form)

    @staticmethod
    @app.route("/reset_password/<token>", methods=['GET', 'POST'])
    def reset_token(token):
        if current_user.is_authenticated:
            return redirect(url_for('account'))
        user = User.verify_reset_token(token)
        if not user:
            flash('That is an invalid or expired token', 'warning')
            return redirect(url_for('reset_request'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated! You are now able to log in.', 'info')
            return redirect(url_for('login'))
        return render_template('reset_token.html', title='Reset Password', form=form)

if __name__=='__main__':
    LvivAssist.run(app.run(debug=True))
