from flask import Flask, render_template, request
app = Flask(__name__)

from flask.ext.bower import Bower
Bower(app)

from ncbi import NCBISearch
import json


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search/', methods=["POST"])
def search():
    search_obj = NCBISearch(request.form["search_term"])
    search_obj.run()
    return json.dumps(search_obj.articles_by_year())

if __name__ == "__main__":
    app.run()
