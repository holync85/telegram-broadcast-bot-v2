
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os
import json
import threading
import http.server
import socketserver
import time

load_dotenv()

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
    try:
        repo_url = os.getenv("GITHUB_REPO_URL")
        branch = os.getenv("GITHUB_BRANCH", "main")
        os.system("git add subscribers.json")
        os.system('git commit -m "Update subscribers list"')
        token = os.getenv("GITHUB_TOKEN")
        repo_path = os.getenv("GITHUB_REPO_URL")
        branch = os.getenv("GITHUB_BRANCH", "main")
        push_url = f"https://{token}@{repo_path}"
        os.system(f"git push {push_url} {branch}")
    except Exception as e:
        print("Git push failed:", e)

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in subscribers:
        subscribers.add(user_id)
        save_subscribers()
    update.message.reply_text("✅ 你已订阅")

def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 无权限")
    message = ' '.join(context.args)
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_message(chat_id=uid, text=message)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 文字发送 {success} 人，失败 {fail} 人")

def broadcastpic(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 1:
        return update.message.reply_text("用法：/broadcastpic 图片链接")
    url = context.args[0]
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_photo(chat_id=uid, photo=url)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 图片发送 {success} 人，失败 {fail} 人")

def broadcastvideo(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 1:
        return update.message.reply_text("用法：/broadcastvideo 视频链接")
    url = context.args[0]
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_video(chat_id=uid, video=url)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 视频发送 {success} 人，失败 {fail} 人")

def broadcastvoice(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 1:
        return update.message.reply_text("用法：/broadcastvoice 音频链接")
    url = context.args[0]
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_voice(chat_id=uid, voice=url)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 语音发送 {success} 人，失败 {fail} 人")

def broadcastfull(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 2:
        return update.message.reply_text("用法：/broadcastfull 图片链接 说明")
    url = context.args[0]
    caption = ' '.join(context.args[1:])
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_photo(chat_id=uid, photo=url, caption=caption)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 图片+说明发送 {success} 人，失败 {fail} 人")

def broadcastbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 3:
        return update.message.reply_text("用法：/broadcastbtn 图片链接 按钮说明 按钮链接")
    url = context.args[0]
    link = context.args[-1]
    caption = ' '.join(context.args[1:-1])
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(caption, url=link)]])
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_photo(chat_id=uid, photo=url, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 图片+按钮发送 {success} 人，失败 {fail} 人")

def broadcastvidbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 3:
        return update.message.reply_text("用法：/broadcastvidbtn 视频链接 按钮说明 按钮链接")
    url = context.args[0]
    link = context.args[-1]
    caption = ' '.join(context.args[1:-1])
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(caption, url=link)]])
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_video(chat_id=uid, video=url, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 视频+按钮发送 {success} 人，失败 {fail} 人")


def broadcastpicbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 4:
        return update.message.reply_text("用法：/broadcastpicbtn 图片链接 说明文字 按钮文字 按钮链接")
    url = context.args[0]
    caption = context.args[1]
    btn_text = context.args[2]
    link = context.args[3]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=link)]])
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_photo(chat_id=uid, photo=url, caption=caption, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 图片+说明+按钮发送 {success} 人，失败 {fail} 人")

def broadcastvidfullbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args) < 4:
        return update.message.reply_text("用法：/broadcastvidfullbtn 视频链接 说明文字 按钮文字 按钮链接")
    url = context.args[0]
    caption = context.args[1]
    btn_text = context.args[2]
    link = context.args[3]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(btn_text, url=link)]])
    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_video(chat_id=uid, video=url, caption=caption, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)
    update.message.reply_text(f"✅ 视频+说明+按钮发送 {success} 人，失败 {fail} 人")

def list_users(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    uids = "\n".join(str(i) for i in subscribers)
    update.message.reply_text(f"订阅用户：\n{uids or '暂无'}")


def count_subscribers(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    update.message.reply_text(f"当前订阅人数：{len(subscribers)}")

def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

def main():
    threading.Thread(target=keep_alive).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("broadcastpic", broadcastpic))
    dp.add_handler(CommandHandler("broadcastvideo", broadcastvideo))
    dp.add_handler(CommandHandler("broadcastvoice", broadcastvoice))
    dp.add_handler(CommandHandler("broadcastfull", broadcastfull))
    dp.add_handler(CommandHandler("broadcastbtn", broadcastbtn))
    dp.add_handler(CommandHandler("broadcastvidbtn", broadcastvidbtn))
    dp.add_handler(CommandHandler("list", list_users))
    dp.add_handler(CommandHandler("count", count_subscribers))
    dp.add_handler(CommandHandler("broadcastpicbtn", broadcastpicbtn))
    dp.add_handler(CommandHandler("broadcastvidfullbtn", broadcastvidfullbtn))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
