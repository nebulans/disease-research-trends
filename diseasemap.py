from flask import Flask, render_template
app = Flask(__name__)

from flask.ext.bower import Bower
Bower(app)

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
