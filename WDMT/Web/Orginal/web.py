from flask import Flask
from flask import render_template, request

CMT_DB = "static/text/text.txt"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():    
    file = open(CMT_DB, 'r')
    content = file.readlines()
    return render_template("index.html", comments=content)


@app.route("/", methods=["POST"])
def cmtHandler():
    if request.method == "POST":
        comment = request.form.get("comment")
        file = open(CMT_DB, 'a')
        file.write(comment+"\n")
        file.close()
    return index()