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
    search_term = request.form.get("search_term")
    search_start = request.form.get("search_start", "1800")
    if not search_start:
        search_start = "1800"
    search_end = request.form.get("search_end", "2016")
    if not search_end:
        search_end = "2016"
    search_obj = NCBISearch(search_term, dates=(search_start, search_end))
    search_obj.run()
    data = {"articlesPerYear": []}
    articles_per_year = search_obj.articles_by_year()
    for year in range(min(*articles_per_year.keys()), max(*articles_per_year.keys()) + 1):
        data["articlesPerYear"].append({"year": year, "articles": articles_per_year.get(year, 0)})
    data["queryDetails"] = query_details(search_obj)
    return json.dumps(data)

def query_details(search_object):
    data = {
        "results": search_object.results
    }
    return render_template("query_details.html", **data)


if __name__ == "__main__":
    app.run()
