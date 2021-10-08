import json
from telebot import TeleBot, types
from telebot.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton

# Custom imports
from Constants import DataDirectory, FAQScriptName
from Category import Category
from FileIO import LoadScript

# Load credentials
credentialsFile = open(DataDirectory + "Credentials.json", "r")
credentials = json.load(credentialsFile)
credentialsFile.close()

# Create bot
bot = TeleBot(credentials["token"])

# Script and state data
UserStates = {}
FAQScript = Category("Main", "What would you like to know?")
    

def SendMessage(user, message, reply_markup = None):
    mType = type(message)
    if mType is str:
        bot.send_message(user, message, reply_markup=reply_markup)
    elif mType is InputMediaPhoto or mType is InputMediaVideo:
        # Send media
        bot.send_media_group(user, [message])

        # Send message after media
        bot.send_message(user, message.caption, reply_markup=reply_markup)

        # Close media file
        message.media.close()


def SendMedia(user):
    # Send image
    img1 = open(DataDirectory + "Chigua.png", "rb")
    bot.send_media_group(user, [InputMediaPhoto(img1, "Caption 1")])
    img1.close()


def SendMediaGroup(user):
    # Send image
    img1 = open(DataDirectory + "Chigua.png", "rb")
    img2 = open(DataDirectory + "clowntoclown.jpg", "rb")
    imgs = [InputMediaPhoto(img1, "Test Caption 1"), InputMediaPhoto(img2, "Test Caption 2")]
    bot.send_media_group(user, imgs)
    img1.close()
    img2.close()


def GenerateReplyMarkup():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Test reply button", callback_data="test"))


# Capture all text messages that are not commands
@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
def AnyTextMessage(m):
    SendMessage(m.chat.id, "What?")


### Command handling ###

@bot.message_handler(commands=["start"])
def Start_Command(m):
    # Send main message
    message, markup = FAQScript.Selected(None)
    SendMessage(m.chat.id, message, markup)


@bot.message_handler(commands=["media"])
def Media_Command(m):
    # Send media
    SendMedia(m.chat.id)


@bot.message_handler(commands=["mediagroup"])
def Media_Command(m):
    # Send media
    SendMediaGroup(m.chat.id)

### End of command handling ###


@bot.callback_query_handler(lambda query : query.data != "")
def Test_Callback(query):
    message, markup = FAQScript.Selected(query.data)
    SendMessage(query.message.chat.id, message, markup)


### Bot execution starts here
# Load FAQ script
LoadScript(DataDirectory + FAQScriptName, FAQScript)

# Start polling for messages
bot.polling(none_stop=True)