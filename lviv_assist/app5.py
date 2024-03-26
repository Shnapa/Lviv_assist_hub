from flask import Flask, render_template, request
from users_database import show_employees, get_hashtags


app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index_search.html", hashtags=list(set(get_hashtags())))

@app.route("/get_companies")
def get_companies():
    hashtag = request.args.get('hashtag')
    return show_employees(hashtag)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
