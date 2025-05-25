
import json
import subprocess
import os
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SUBSCRIBE_FILE = "subscribe.json"

# 载入订阅者
try:
    with open(SUBSCRIBE_FILE, "r") as f:
        subscribers = json.load(f)
except:
    subscribers = []

def save_subscribers():
    with open(SUBSCRIBE_FILE, "w") as f:
        json.dump(subscribers, f)
    git_push()

def git_push():
    repo_dir = os.getcwd()
    subprocess.run(["git", "config", "--global", "user.email", "render@bot.com"])
    subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])
    subprocess.run(["git", "add", SUBSCRIBE_FILE], cwd=repo_dir)
    subprocess.run(["git", "commit", "-m", "Auto update subscribe.json"], cwd=repo_dir)
    subprocess.run(["git", "push", f"https://{GITHUB_TOKEN}@{GITHUB_REPO}"], cwd=repo_dir)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    user_id = request.json.get("user_id")
    if user_id and user_id not in subscribers:
        subscribers.append(user_id)
        save_subscribers()
        return "Subscribed", 200
    return "Already subscribed or invalid", 400

@app.route("/unsubscribe", methods=["POST"])
def unsubscribe():
    user_id = request.json.get("user_id")
    if user_id and user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers()
        return "Unsubscribed", 200
    return "Not subscribed or invalid", 400

@app.route("/subscribers", methods=["GET"])
def get_subscribers():
    return json.dumps(subscribers), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
