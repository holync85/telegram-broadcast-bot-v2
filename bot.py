from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import json
import threading
import http.server
import socketserver

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

FILE_PATH = "subscribers.json"
subscribers = set()

if os.path.exists(FILE_PATH):
    with open(FILE_PATH, "r") as f:
        subscribers = set(json.load(f))

def save_subscribers():
    with open(FILE_PATH, "w") as f:
        json.dump(list(subscribers), f)

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    subscribers.add(user_id)
    save_subscribers()
    update.message.reply_text("✅ 你已订阅")

def broadcastvidbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 3:
        return update.message.reply_text("用法：/broadcastvidbtn 视频链接 说明 按钮URL")
    video_url = context.args[0]
    caption = context.args[1]
    link = context.args[2]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("点击查看", url=link)]])
    success, fail = 0, 0
    for uid in subscribers:
        try:
            context.bot.send_video(chat_id=uid, video=video_url, caption=caption, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
    update.message.reply_text(f"✅ 视频+按钮发送成功 {success}，失败 {fail}")

def list_users(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    uids = "\n".join(str(i) for i in subscribers)
    update.message.reply_text(f"订阅用户：\n{uids or '暂无'}")

def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

def main():
    threading.Thread(target=keep_alive).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("broadcastvidbtn", broadcastvidbtn))
    dp.add_handler(CommandHandler("list", list_users))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
