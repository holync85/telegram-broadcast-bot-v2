from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os
import json
import threading
import http.server
import socketserver
import time
import base64
import requests

load_dotenv()

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO", "holync85/telegram-broadcast-bot-v2")
FILE_PATH = "subscribers.json"
GITHUB_API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
subscribers = set()

def load_subscribers():
    global subscribers
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(GITHUB_API_URL, headers=headers)
    if res.status_code == 200:
        content = res.json()["content"]
        decoded = base64.b64decode(content).decode("utf-8")
        subscribers = set(json.loads(decoded))
    else:
        subscribers = set()

def save_subscribers():
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/json"
    }
    get_res = requests.get(GITHUB_API_URL, headers=headers)
    sha = get_res.json().get("sha") if get_res.status_code == 200 else None

    content = base64.b64encode(json.dumps(list(subscribers)).encode("utf-8")).decode("utf-8")
    data = {
        "message": "Update subscribers list",
        "content": content,
        "branch": "main"
    }
    if sha:
        data["sha"] = sha

    res = requests.put(GITHUB_API_URL, headers=headers, data=json.dumps(data))
    print("✅ GitHub 更新成功" if res.status_code in [200, 201] else f"❌ GitHub 更新失败: {res.text}")

def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id not in subscribers:
        subscribers.add(user_id)
        save_subscribers()
    update.message.reply_text("Done ✅")

def stop(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id in subscribers:
        subscribers.remove(user_id)
        save_subscribers()
        update.message.reply_text("Cancel ❌")

def broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return update.message.reply_text("❌ 无权限")
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

def list_users(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    uids = "\n".join(str(i) for i in subscribers)
    update.message.reply_text(f"订阅用户：\n{uids or '暂无'}")

def count_subscribers(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID: return
    update.message.reply_text(f"当前订阅人数：{len(subscribers)}")


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
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 无权限")

    if len(context.args) < 2:
        return update.message.reply_text("用法：/broadcastpicbtn 图片链接 说明文字")

    url = context.args[0]
    caption = ' '.join(context.args[1:])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Booking Now", url="https://t.me/jbescort7")],
        [InlineKeyboardButton("📞 WhatsApp", url="https://wa.me/60103741446?text=PM_JB")],
        [InlineKeyboardButton("📞 WhatsApp 2", url="https://wa.me/601157752859?text=PM_JB")],
        [InlineKeyboardButton("🧑‍💻 Live Booking", url="https://go.crisp.chat/chat/embed/?website_id=67d3163f-bdc3-4f3c-a603-e13ab2c65730")]
    ])

    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_photo(chat_id=uid, photo=url, caption=caption, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)

    update.message.reply_text(f"✅ 图片+说明+固定按钮发送 {success} 人，失败 {fail} 人")


def broadcastalbumbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 无权限")

    # 解析参数：<url1> <url2> ... <urlN> -- <caption>
    if len(context.args) < 4 or "--" not in context.args:
        return update.message.reply_text("用法：/broadcastalbumbtn url1 url2 ... urlN -- 说明文字（至少2张，最多10张）")

    sep_idx = context.args.index("--")
    urls = context.args[:sep_idx]
    caption = " ".join(context.args[sep_idx + 1:]).strip()

    if len(urls) < 2:
        return update.message.reply_text("请至少提供 2 个图片链接。")
    if len(urls) > 10:
        return update.message.reply_text("相册一次最多 10 张图片，请减少数量。")

    # 构建相册媒体（只有第一张带 caption）
    media = []
    for i, u in enumerate(urls):
        if i == 0:
            media.append(InputMediaPhoto(media=u, caption=caption))
        else:
            media.append(InputMediaPhoto(media=u))

    # 固定按钮
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Booking Now", url="https://t.me/jbescort7")],
        [InlineKeyboardButton("📞 WhatsApp", url="https://wa.me/60103741446?text=PM_JB")],
        [InlineKeyboardButton("📞 WhatsApp 2", url="https://wa.me/601157752859?text=PM_JB")],
        [InlineKeyboardButton("🧑‍💻 Live Booking", url="https://go.crisp.chat/chat/embed/?website_id=67d3163f-bdc3-4f3c-a603-e13ab2c65730")]
    ])

    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            # 1) 发送相册
            context.bot.send_media_group(chat_id=uid, media=media)
            # 2) 发送按钮消息（不重复说明文字，避免两条都显示长文本）
            context.bot.send_message(chat_id=uid, text="👇 点击下面按钮预约/联系", reply_markup=keyboard)
            success += 1
        except Exception as e:
            # 如果单人失败，计数即可，不中断整体广播
            fail += 1
        time.sleep(0.5)  # 轻微节流，避免触发限速

    update.message.reply_text(f"✅ 相册+按钮发送 {success} 人，失败 {fail} 人")
    

def broadcastvidfullbtn(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return update.message.reply_text("❌ 无权限")

    if len(context.args) < 2:
        return update.message.reply_text("用法：/broadcastvidfullbtn 视频链接 说明文字")

    url = context.args[0]
    caption = ' '.join(context.args[1:])

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📍 Booking Now", url="https://t.me/jbescort7")],
        [InlineKeyboardButton("📞 WhatsApp", url="https://wa.me/60103741446?text=PM_JB")],
        [InlineKeyboardButton("📞 WhatsApp 2", url="https://wa.me/601157752859?text=PM_JB")],
        [InlineKeyboardButton("🧑‍💻 Live Booking", url="https://go.crisp.chat/chat/embed/?website_id=67d3163f-bdc3-4f3c-a603-e13ab2c65730")]
    ])

    success, fail = 0, 0
    for uid in list(subscribers):
        try:
            context.bot.send_video(chat_id=uid, video=url, caption=caption, reply_markup=keyboard)
            success += 1
        except:
            fail += 1
        time.sleep(0.5)

    update.message.reply_text(f"✅ 视频+说明+固定按钮发送 {success} 人，失败 {fail} 人")




def jb_hot_area(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("CIQ", url="https://www.jbescortsvc.com/jb-hot-area/ciq")],
        [InlineKeyboardButton("Sri Yaacob", url="https://www.jbescortsvc.com/jb-hot-area/sri-yaacob")],
    ])
    update.message.reply_text("Click Area：", reply_markup=keyboard)


def jb_1_area(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Bukit Indah", url="https://www.jbescortsvc.com/jb-1-area/bukit-indah-1")],
        [InlineKeyboardButton("Desa Tebrau", url="https://www.jbescortsvc.com/jb-1-area/desa-tebrau-1")],
        [InlineKeyboardButton("JB Town", url="https://www.jbescortsvc.com/jb-1-area/jb-town-2")],
        [InlineKeyboardButton("Kebun Teh", url="https://www.jbescortsvc.com/jb-1-area/kebun-teh")],
        [InlineKeyboardButton("Nusa Bestari", url="https://www.jbescortsvc.com/jb-1-area/nusa-bestari")],
        [InlineKeyboardButton("Nusa Bestari 2", url="https://www.jbescortsvc.com/jb-1-area/nusa-bestari-2")],
    ])
    update.message.reply_text("Click Area：", reply_markup=keyboard)


def jb_2_area(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Bukit Indah", url="https://www.jbescortsvc.com/jb-2-area/bukit-indah")],
        [InlineKeyboardButton("Desa Tebrau", url="https://www.jbescortsvc.com/jb-2-area/desa-tebrau")],
        [InlineKeyboardButton("JB Town", url="https://www.jbescortsvc.com/jb-2-area/jb-town")],       
        [InlineKeyboardButton("KSL", url="https://www.jbescortsvc.com/jb-2-area/ksl")],
        [InlineKeyboardButton("Mount Austin", url="https://www.jbescortsvc.com/jb-2-area/mount-austin-1")], 
        [InlineKeyboardButton("Pelangi", url="https://www.jbescortsvc.com/jb-2-area/pelangi")],
        [InlineKeyboardButton("Skudai", url="https://www.jbescortsvc.com/jb-2-area/skudai")],
        [InlineKeyboardButton("Taman Daya", url="https://www.jbescortsvc.com/jb-2-area/taman-daya")],
    ])
    update.message.reply_text("Click Area：", reply_markup=keyboard)

def jb_3_area(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Pelangi", url="https://www.jbescortsvc.com/jb-3-area/pelangi-1")],
        [InlineKeyboardButton("Nusa Bestari(Ctm Chinese Only)", url="https://www.jbescortsvc.com/jb-3-area/nusa-bestari-cn")],
        [InlineKeyboardButton("R&F(Ctm Chinese Only)", url="https://www.jbescortsvc.com/jb-3-area/r-f-cn")],
    ])
    update.message.reply_text("Click Area：", reply_markup=keyboard)
    

def booking(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("WhatsApp", url="https://wa.me/60103741446?text=PM_JB")],
        [InlineKeyboardButton("WhatsApp 2", url="https://wa.me/601157752859?text=PM_JB")],
        [InlineKeyboardButton("Telegram Admin", url="https://t.me/jbescort7")],
        [InlineKeyboardButton("Live Admin", url="https://go.crisp.chat/chat/embed/?website_id=67d3163f-bdc3-4f3c-a603-e13ab2c65730")],     
    ])
    update.message.reply_text("Click Area：", reply_markup=keyboard)


def keep_alive():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", 8080), handler) as httpd:
        httpd.serve_forever()

def main():
    load_subscribers()
    threading.Thread(target=keep_alive).start()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("broadcastpic", broadcastpic))
    dp.add_handler(CommandHandler("broadcastvideo", broadcastvideo))
    dp.add_handler(CommandHandler("broadcastvoice", broadcastvoice))
    dp.add_handler(CommandHandler("broadcastfull", broadcastfull))
    dp.add_handler(CommandHandler("broadcastbtn", broadcastbtn))
    dp.add_handler(CommandHandler("broadcastvidbtn", broadcastvidbtn))
    dp.add_handler(CommandHandler("broadcastpicbtn", broadcastpicbtn))
    dp.add_handler(CommandHandler("broadcastalbumbtn", broadcastalbumbtn))
    dp.add_handler(CommandHandler("broadcastvidfullbtn", broadcastvidfullbtn))
    dp.add_handler(CommandHandler("list", list_users))
    dp.add_handler(CommandHandler("count", count_subscribers))
    dp.add_handler(CommandHandler("jbhot", jb_hot_area))
    dp.add_handler(CommandHandler("jb1", jb_1_area))
    dp.add_handler(CommandHandler("jb2", jb_2_area))
    dp.add_handler(CommandHandler("jb3", jb_3_area))
    dp.add_handler(CommandHandler("booking", booking))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
