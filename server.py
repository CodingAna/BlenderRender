from flask import Flask, render_template, request, send_file, redirect, Response
import subprocess, os, json, random, hashlib, time, werkzeug

BLENDER_EXECUTABLE = "/home/lukas/Downloads/blender-2.93.6-linux-x64/blender"
USER_DIR = "/home/lukas/Dokumente/GitHub/BlenderRender/Users"
DATA_DIR = "/home/lukas/Dokumente/GitHub/BlenderRender/Data"
TOKEN_DURABILITY = 1 * 60 * 60 * 6 # 1s 1min 1h 6h

app = Flask(__name__)

users = []
if os.path.exists(DATA_DIR + "/users.json"):
    with open(DATA_DIR + "/users.json") as f:
        users = json.loads(f.read())

orders = []
if os.path.exists(DATA_DIR + "/orders.json"):
    with open(DATA_DIR + "/orders.json") as f:
        orders = json.loads(f.read())

processes = []
if os.path.exists(DATA_DIR + "/processes.json"):
    with open(DATA_DIR + "/processes.json") as f:
        processes = json.loads(f.read())

def check_token(token: str) -> bool:
    if token == None: return False
    for user in users:
        user_token, user_token_time = user["token"].split("_")
        if user_token == token:
            if user_token_time <= int(time.time()):
                return user
            return False
    return False

def generate_token(length: int = 16) -> str:
    words = "ABCDEFGHIJKLMNOPWRSTUVWXYZabcdefghijklmnopwrstuvwxyz0123456789"
    out = "".join(random.choice(words) for _ in range(length))
    return out

def generate_id(length: int = 12):
    words = "ABCDEFGHIJKLMNOPWRSTUVWXYZabcdefghijklmnopwrstuvwxyz0123456789"
    out = "".join(("-" if _ % 4 == 0 and _ != 0 else "") + random.choice(words) for _ in range(length))
    return out

def get_orders(user_id: str) -> list:
    out = []
    for order in orders:
        if order["from"] == user_id:
            out.append(order)
    return out

def valid_password(password: str) -> bool:
    if len(password) < 8: return False
    valid = [0, 0, 0]
    nums = [x for x in range(10)]
    for c in nums:
        if str(c) in password: valid[0] += 1
    chars = "".join(chr(65 + x) for x in range(26))
    for c in chars:
        if str(c) in password: valid[1] += 1
    chars = "".join(chr(97 + x) for x in range(26))
    for c in chars:
        if str(c) in password: valid[2] += 1

    #      Numbers           Capital letter    Letter
    return valid[0] >= 2 and valid[1] >= 1 and valid[2] >= 5

def get_user_position(user_id: str) -> int:
    i = 0
    for user in users:
        if user["id"] == user_id:
            return i
        i += 1
    return -1

def refresh_token_timeout(token: str) -> bool:
    user = check_token(token)
    if user:
        pos = get_user_position(user["id"])
        users[pos]["token"] = token + "_" + str(int(time.time()) + TOKEN_DURABILITY)
        return True
    return False

@app.route("/")
def index():
    cookies = request.cookies
    token = cookies.get("token")
    print(token)
    user = check_token(token)
    print(user)
    if user:
        refresh_token_timeout(token)
        user_orders = get_orders(user["id"])
        return render_template("index.html", username=user["username"], orders=user_orders)
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def route_login():
    if request.method == "GET":
        return render_template("login.html")

    data = json.loads(request.data.decode("UTF-8"))
    if data.get("type") == "login":
        userdata = data.get("userdata")
        hash3 = hashlib.sha3_512()
        i = 0
        for user in users:
            hash3.update((user["username"] + user["password"]).encode())
            h = hash3.hexdigest()
            if h == userdata:
                token = generate_token()
                resp = Response(redirect("/"))
                resp.set_cookie("token", token)
                users[i]["token"] = token + "_" + str(int(time.time()) + TOKEN_DURABILITY)
                #return resp
                return token
            i += 1

        #return render_template("login.html", error="credentials")
        return "credentials"

    elif data.get("type") == "register":
        userdata = data.get("userdata")
        username = data.get("username")
        password = data.get("password")
        if not valid_password(password):
            #return render_template("login.html", error="password")
            return password

        hash3 = hashlib.sha3_512()
        i = 0
        for user in users:
            if user["username"] == username:
                #return render_template("login.html", error="exists")
                return "exists"
            i += 1

        hash3.update((username + password).encode())
        if not hash3.hexdigest() == userdata:
            return "userdata"

        token = generate_token()
        user = {
            "id": generate_id(),
            "username": username,
            "password": password,
            "token": token + "_" + str(int(time.time()) + TOKEN_DURABILITY)
        }
        users.append(user)
        resp = Response(redirect("/"))
        resp.set_cookie("token", token)
        #return resp
        print(token)
        print(users)
        return token # Send data in JSON format

    #return render_template("login.html", error="unknown")
    return "unknown"

@app.route("/create_order", methods=["POST"])
def route_create_order():
    cookies = request.cookies
    token = cookies.get("token") # or get "userdata" from data if this isn't working
    user = check_token(token)
    if user:
        refresh_token_timeout(token)
        user_id = user["id"]

        file = request.files["file"]
        filename = werkzeug.utils.secure_filename(file.filename)
        if filename == "":
            return Response("file", 400)

        if not os.path.exists(f"{DATA_DIR}/{user_id}"):
            os.mkdir(f"{DATA_DIR}/{user_id}")
        file.save(f"{DATA_DIR}/{user_id}/{filename}")

        command = f"{BLENDER_EXECUTABLE} -b -P ./use_gpu.py {DATA_DIR}/{user_id}/{filename} -E CYCLES -t 0 -o {DATA_DIR}/{user_id}/{filename}_#.png -f 1"
        process = subprocess.Popen(command.split())
        pid = generate_id()
        
        processes.append({ # Maybe use dict instead of list for faster access
            "id": pid,
            "process": process
        })

        orders.append({
            "name": filename,
            "id": generate_id(),
            "from": user_id,
            "timestamp": time.time(),
            "process_id": pid,
            "rendered": True
        })

        if request.method == "GET": return redirect("/")
        elif request.method == "POST": return "success"
    if request.method == "GET": return redirect("/login")
    elif request.method == "POST": return Response("token", 401)

@app.route("/get_progress", methods=["POST"])
def route_get_progress():
    # order_id needed
    # faster access for better
    return "1"

@app.route("/download/<order_id>")
def route_download(order_id: str):
    cookies = request.cookies
    token = cookies.get("token") # or get "userdata" from data if this isn't working
    user = check_token(token)
    if user:
        refresh_token_timeout(token)
        user_id = user["id"]
        user_orders = get_orders(user["id"])
        for order in user_oders:
            if order["id"] == order_id:
                order_name = order["name"]
                if os.path.isfile(f"{DATA_DIR}/{user_id}/{order_name}_1.png"):
                    return send_file(f"{DATA_DIR}/{user_id}/{order_name}_1.png", cache_timeout=0)
                else: return Response("This file does not exist.", 404)
        return Response("forbidden", 401)
    return redirect("/login")

app.run(host="0.0.0.0", port=80)
