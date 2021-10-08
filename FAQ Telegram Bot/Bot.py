# Python libs import
import json

# Telebot imports
from telebot import TeleBot
from telebot.types import InputMediaPhoto, InputMediaVideo

# Class imports
from Category import Category

# Constant imports
from Constants import DataDirectory, FAQScriptName

# Method imports
from FileIO import LoadScript


### Script and state data ###
UserStates = {}
FAQScript = Category("Main", "What would you like to know?", True)

### Load credentials ###
credentialsFile = open(DataDirectory + "Credentials.json", "r")
credentials = json.load(credentialsFile)
credentialsFile.close()

# Create bot
bot = TeleBot(credentials["token"])
    

# Universal message sending function
def SendMessage(user, message, reply_markup = None):
    mType = type(message)
    if mType is str:
        bot.send_message(user, message, reply_markup=reply_markup)
    elif mType is InputMediaPhoto or mType is InputMediaVideo:
        # Send media
        caption = message.caption
        message.caption = None
        bot.send_media_group(user, [message])

        # Send message after media
        bot.send_message(user, caption, reply_markup=reply_markup)

        # Close media file
        message.media.close()


# Capture all text messages that are not commands
@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
def AnyTextMessage(m):
    SendMessage(m.chat.id, "What?")


### Command handling ###

@bot.message_handler(commands=["start"])
def Start_Command(m):
    ### Send main message ###
    # Retrieve message and markup
    message, markup, newState = FAQScript.Selected(None, [])

    # Reset user state
    user = m.chat.id
    UserStates[user] = []

    # Send message
    SendMessage(user, message, markup)

### End of command handling ###


@bot.callback_query_handler(lambda query : query.data != "")
def FAQ_Callback(query):
    # Fetch user id
    user = query.message.chat.id

    # Fetch message and markup
    message, markup, newState = FAQScript.Selected(query.data, UserStates[user] if user in UserStates else [])

    # Update new state
    UserStates[user] = newState

    # Send message
    SendMessage(user, message, markup)


### Bot execution starts here
# Load FAQ script
LoadScript(DataDirectory + FAQScriptName, FAQScript)

# Start polling for messages
bot.polling(none_stop=True)