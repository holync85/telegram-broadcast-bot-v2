
import telebot

BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "欢迎来到 JB ESCORT 服务，请选择菜单或输入命令。")

@bot.message_handler(commands=['photos'])
def send_photos(message):
    bot.send_photo(message.chat.id, open('service.jpg', 'rb'))

@bot.message_handler(commands=['contact'])
def send_contact(message):
    bot.send_message(message.chat.id, "联系客服：@yourusername")

@bot.message_handler(commands=['website'])
def send_website(message):
    bot.send_message(message.chat.id, "官网：https://www.jbescortsvc.com")

bot.polling()
