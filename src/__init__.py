from flask import Flask, render_template, request

from .data import photos

app = Flask(__name__, template_folder="templates", static_folder="static")
# Default browser cache to 5 minutes
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 300


@app.route("/")
def index():
    return render_template("index.html", photos=photos)


@app.route("/order")
def order():
    return render_template("order.html", photo=photos.get(request.args.get("photo_id")))


@app.errorhandler(404)
def handle_404(e):
    return render_template("404.html")
