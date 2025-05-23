from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import json
import requests
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
    update.message.reply_text("✅ 你已订阅，之后我会向你发送消息。")

def stop(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers()
        update.message.reply_text("你已取消订阅。")

def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 你没有权限广播消息。")
    message = ' '.join(context.args)
    if not message:
        return update.message.reply_text("请输入要广播的消息内容")
    success, fail = 0, 0
    for user_id in list(subscribers):
        try:
            context.bot.send_message(chat_id=user_id, text=message)
            success += 1
        except:
            fail += 1
    update.message.reply_text(f"✅ 已发送给 {success} 人，失败 {fail} 人")

def broadcast_image(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 你没有权限发送图片。")
    if len(context.args) == 0:
        return update.message.reply_text("请输入图片URL，如：/broadcastpic https://...")
    image_url = context.args[0]
    success, fail = 0, 0
    for user_id in list(subscribers):
        try:
            context.bot.send_photo(chat_id=user_id, photo=image_url)
            success += 1
        except:
            fail += 1
    update.message.reply_text(f"✅ 图片已发送 {success} 人，失败 {fail} 人")

def broadcast_full(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 你没有权限。")
    if len(context.args) < 2:
        return update.message.reply_text("格式：/broadcastfull 图片URL 文字说明")
    image_url = context.args[0]
    caption = ' '.join(context.args[1:])
    success, fail = 0, 0
    for user_id in list(subscribers):
        try:
            context.bot.send_photo(chat_id=user_id, photo=image_url, caption=caption)
            success += 1
        except:
            fail += 1
    update.message.reply_text(f"✅ 图片+文字已发 {success} 人，失败 {fail} 人")

def broadcast_button(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 无权限")
    if len(context.args) < 3:
        return update.message.reply_text("格式：/broadcastbtn 图片URL 说明 按钮链接")
    image_url = context.args[0]
    caption = context.args[1]
    btn_url = context.args[2]
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("点击查看", url=btn_url)]])
    success, fail = 0, 0
    for user_id in list(subscribers):
        try:
            context.bot.send_photo(chat_id=user_id, photo=image_url, caption=caption, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
    update.message.reply_text(f"✅ 带按钮已发送 {success} 人，失败 {fail} 人")

def list_subscribers(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return
    user_list = '\n'.join(str(uid) for uid in subscribers)
    update.message.reply_text(f"订阅用户：\n{user_list or '暂无'}")

def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        print("Keep-alive server running at port 8080...")
        httpd.serve_forever()

def main():
    threading.Thread(target=keep_alive).start()
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("broadcastpic", broadcast_image))
    dp.add_handler(CommandHandler("broadcastfull", broadcast_full))
    dp.add_handler(CommandHandler("broadcastbtn", broadcast_button))
    dp.add_handler(CommandHandler("list", list_subscribers))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
