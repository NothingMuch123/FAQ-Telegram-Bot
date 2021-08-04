import json
from telebot import TeleBot, types


# Load credentials
credentials = json.load(open("FAQ Telegram Bot/Data/Credentials.json", "r"))

# Create bot
bot = bot = TeleBot(credentials["token"])
    

def SendMessage(user, message):
    bot.send_message(user, message)


@bot.message_handler(commands=['start'])
def Start_Command(m):
    SendMessage(m.chat.id, "Test message")


# Start polling for messages
bot.polling(none_stop=True)