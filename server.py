from flask import Flask, render_template, request, send_file
import subprocess, os

BLENDER_EXECUTABLE = "/home/lukas/Downloads/blender-2.93.6-linux-x64/blender"
USER_DIR = "~/Dokumente/Websites/BlenderRender/Users"
DATA_DIR = "~/Dokumente/Websites/BlenderRender/Data"

app = Flask(__name__)

users = {
    "MerlinHof": {
        "id": "ABCD-EFGH",
        "pass": "BlenderRender123",
        "orders": {}
    }
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/profile")
def route_profile():
    # Use cookies instead
    # Use Jinja2 in HTML files for nice <a>'s in an <ul/ol>
    return users.get(data.get("username"))["orders"]

@app.route("render", method=["POST"])
def route_render():
    user = users.get(data.get("username"))
    if user == None: return "invalid username"
    user_id = user["id"]

    order_id = user["orders"].get(data.get("order_id"))
    if order_id == None: return "invalid order_id"

    command = f"{BLENDER_EXECUTABLE} -b {DATA_DIR}/{user_id}/{order_id}.blend -o {DATA_DIR}/{user_id}/{order_id}_#.png -f 1"
    subprocess.Popen(command.split())

    return "Started rendering. Download the result in your profile."

@app.route("/download")
def route_download():
    if os.path.isfile(f"{DATA_DIR}/{user_id}/{order_id}_1.png"):
        return send_file(f"{DATA_DIR}/{user_id}/{order_id}_1.png", cache_timeout=0)
    else: return "this file does not exist"
