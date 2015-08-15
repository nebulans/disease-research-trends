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
    data = {"articlesPerYear": []}
    articles_per_year = search_obj.articles_by_year()
    for year in range(min(*articles_per_year.keys()), max(*articles_per_year.keys()) + 1):
        data["articlesPerYear"].append({"year": year, "articles": articles_per_year.get(year, 0)})
    return json.dumps(data)

if __name__ == "__main__":
    app.run()
