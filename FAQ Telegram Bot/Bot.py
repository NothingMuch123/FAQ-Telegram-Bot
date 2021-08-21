import json
from telebot import TeleBot, types

# Custom imports
from Constants import DataDirectory

# Load credentials
credentials = json.load(open(DataDirectory + "Credentials.json", "r"))

# Create bot
bot = bot = TeleBot(credentials["token"])
    

def SendMessage(user, message, reply_markup = None):
    bot.send_message(user, message, reply_markup=reply_markup)


def SendMediaGroup(user):
    # Send image
    img1 = open(DataDirectory + "Chigua.png", "rb")
    img2 = open(DataDirectory + "clowntoclown.jpg", "rb")
    imgs = [types.InputMediaPhoto(img1, "Test Caption 1"), types.InputMediaPhoto(img2, "Test Caption 2")]
    bot.send_media_group(user, imgs)
    img1.close()
    img2.close()


def GenerateReplyMarkup():
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Test reply button", callback_data="test"))


# Capture all text messages that are not commands
@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
def AnyTextMessage(m):
    SendMessage(m.chat.id, "What?")


@bot.message_handler(commands=["start"])
def Start_Command(m):
    # Send main message
    SendMessage(m.chat.id, "Test message", GenerateReplyMarkup())


@bot.message_handler(commands=["media"])
def Media_Command(m):
    # Send media
    SendMediaGroup(m.chat.id)


@bot.callback_query_handler(lambda query : query.data != "")
def Test_Callback(query):
    SendMessage(query.message.chat.id, "Callback called")


# Start polling for messages
bot.polling(none_stop=True)