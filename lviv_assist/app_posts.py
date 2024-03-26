from flask import Flask, render_template, request
from lviv_assist.users_database import Employee, get_hashtags, add_hashtag_profile

app = Flask(__name__)
employee = Employee()

@app.route('/')
def index():
    hashtags = get_hashtags()
    return render_template("post.html", hashtags=hashtags)

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    description = request.form['description']
    price = request.form['price']
    hashtag = request.form['hashtag']

    add_hashtag_profile(name, surname, email, description, price, hashtag)

    return render_template("success.html")

if __name__ == "__main__":
    app.run(debug=True)
