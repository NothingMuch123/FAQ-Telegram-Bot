# Python libs import
import json

# Telebot imports
from telebot import TeleBot
from telebot.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton

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

admin = False

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


def CreateButton(m,markup,text,callback):
    a = InlineKeyboardButton(text,callback_data= callback)
    markup.add(a)
    return markup

# Capture all text messages that are not commands
@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
def AnyTextMessage(m):
    SendMessage(m.chat.id, "Type /start to begin or /help to find possible commands.")

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
    
    # Send main message
    #SendMessage(m.chat.id, "Welcome!")
    #markup = types.InlineKeyboardMarkup()
    #markup = CreateButton(m, markup, "Press here to begin", 'media')

### End of Command handling ###


### Callback Query handling ###

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

### End of CallBack Query handling ###


### Admin Functions ###

@bot.message_handler(commands=["login"])
def Login_Command(m):
    global admin
    if admin == False:
        if m.text.split(" ")[1] == credentials["password"]:
            admin = True
            AdminLoggedin(m)
        else:
            SendMessage(m.chat.id, "Wrong password, try again.")
    else:
        SendMessage(m.chat.id, "You are already logged in.")

def Check_Password(m):
    if m.text == credentials["password"]:
        AdminLoggedin(m)
    else:
        SendMessage(m.chat.id, "Wrong password, try again.")


def AdminLoggedin(m):
    cid = m.chat.id
    bot.delete_message(cid, m.message_id)
    markup = InlineKeyboardMarkup()
    markup = CreateButton(m, markup, "Edit current questions", 'Edit')
    markup = CreateButton(m, markup, "Create new questions", 'Create')
    markup = CreateButton(m, markup, "Check messages", 'Check')
    bot.send_message(cid, "Password accepted, welcome Administrator.\nWhat would you like to do now?", disable_notification=True, reply_markup=markup)

### End of Admin Functions ###

@bot.message_handler(commands=["help"])
def Help_Command(m):
    # Send media
    SendMessage(m.chat.id, "/start\n/media")


# @bot.callback_query_handler(lambda query : query.data != "")
# def AdminFunctions(query):
#     if query.data == "Edit":
#         SendMessage(query.message.chat.id, "Edit questions.")
#     elif query.data == "Create":
#         SendMessage(query.message.chat.id, "Create new questions.")
#     elif query.data == "Check":
#         SendMessage(query.message.chat.id, "Check messages.")


### Bot execution starts here
# Load FAQ script
LoadScript(DataDirectory + FAQScriptName, FAQScript)
    
# Start polling for messages
bot.polling(none_stop=True)
