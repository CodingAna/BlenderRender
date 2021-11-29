from flask import Flask, render_template, request, send_file, redirect
import subprocess, os

BLENDER_EXECUTABLE = "/home/lukas/Downloads/blender-2.93.6-linux-x64/blender"
USER_DIR = "~/Dokumente/Websites/BlenderRender/Users"
DATA_DIR = "~/Dokumente/Websites/BlenderRender/Data"

app = Flask(__name__)

users = {
    "MerlinHof": {
        "id": "ABCD-EFGH",
        "pass": "BlenderRender123",
        "orders": [],
        "processes": []
    }
}

@app.route("/")
def index():
    cookies = request.cookies

    username = cookies.get("username")
    if username == None: return redirect("/login")

    user = users.get(username)
    if user == None: return "You are not registered."
    orders = user.get("orders")

    return render_template("index.html", username=username, orders=orders)

@app.route("/add_order")
def route_add_order():
    cookies = request.cookies

    username = cookies.get("username")
    if username == None: return redirect("/login")
    if users.get(username) == None: return "You are not registered."

    order = {
        "id": "", # Generate random ID
        "name": "", # Get name from client
        "rendered": False
    }
    users[username]["orders"].append(order)

@app.route("render", method=["POST"])
def route_render():
    user = users.get(data.get("username"))
    if user == None: return "invalid username"
    user_id = user["id"]

    order_id = user["orders"].get(data.get("order_id"))
    if order_id == None: return "invalid order_id"

    command = f"{BLENDER_EXECUTABLE} -b {DATA_DIR}/{user_id}/{order_id}.blend -o {DATA_DIR}/{user_id}/{order_id}_#.png -f 1"
    process = subprocess.Popen(command.split())
    # Add process to user.processes to check status?

    return "Started rendering. Download the result in your profile."

@app.route("/download/<order_id>")
def route_download(order_id: str):
    cookies = request.cookies

    username = cookies.get("username")
    if username == None: return redirect("/login")
    user = users.get(username)
    if not user["orders"].get(order_id):
        return "You are not allowed to download this."

    if os.path.isfile(f"{DATA_DIR}/{user_id}/{order_id}_1.png"):
        return send_file(f"{DATA_DIR}/{user_id}/{order_id}_1.png", cache_timeout=0)
    else: return "This file does not exist."
