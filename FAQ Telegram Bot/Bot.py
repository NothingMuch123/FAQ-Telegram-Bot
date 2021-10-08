import json
from telebot import TeleBot, types


# Custom imports
from Constants import DataDirectory

# Load credentials
credentials = json.load(open(DataDirectory + "Credentials.json", "r"))

# Create bot
bot = bot = TeleBot(credentials["token"])

admin = False

def SendMessage(user, message, reply_markup = None):
    bot.send_message(user, message, reply_markup=reply_markup)

@bot.message_handler(commands=["picture"])
def SendMediaGroup(user):
    # Send image
    img1 = open(DataDirectory + "Fruits.jpg", "rb")
    img2 = open(DataDirectory + "Vegetables.jpg", "rb")
    imgs = [types.InputMediaPhoto(img1, "Fruits"), types.InputMediaPhoto(img2, "Vegetables")]
    bot.send_media_group(user, imgs)
    img1.close()
    img2.close()

def GenerateReplyMarkup(text):
    return types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text, callback_data="test"))

def CreateButton(m,markup,text,callback):
    a = types.InlineKeyboardButton(text,callback_data= callback)
    markup.add(a)
    return markup

#Capture all text messages that are not commands
#@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
#def AnyTextMessage(m):
    SendMessage(m.chat.id, "Command not found, type /start to begin or /help to find possible commands.")

@bot.callback_query_handler(lambda query : query.data != "")
def AdminFunctions(query):
    if query.data == "Edit":
        SendMessage(query.message.chat.id, "Edit questions.")
    elif query.data == "Create":
        SendMessage(query.message.chat.id, "Create new questions.")
    elif query.data == "Check":
        SendMessage(query.message.chat.id, "Check messages.")

@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
def AnyTextMessage(m):
    SendMessage(m.chat.id, "Unknown command.")

@bot.message_handler(commands=["start"])
def Start_Command(m):
    # Send main message
    SendMessage(m.chat.id, "Welcome!")
    markup = types.InlineKeyboardMarkup()
    markup = CreateButton(m, markup, "Press here to begin", 'media')

@bot.message_handler(commands=["media"])
def Media_Command(m):
    # Send media
    SendMediaGroup(m.chat.id)

@bot.message_handler(commands=["help"])
def Help_Command(m):
    # Send media
    SendMessage(m.chat.id, "/start\n/media")

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
    markup = types.InlineKeyboardMarkup()
    markup = CreateButton(m, markup, "Edit current questions", 'Edit')
    markup = CreateButton(m, markup, "Create new questions", 'Create')
    markup = CreateButton(m, markup, "Check messages", 'Check')
    bot.send_message(cid, "Password accepted, welcome Administrator.\nWhat would you like to do now?", disable_notification=True, reply_markup=markup)

@bot.callback_query_handler(lambda query : query.data != "")
def Test_Callback(query):
    SendMessage(query.message.chat.id, "What would you like to do?", GenerateReplyMarkup("Ask for help"))
    
# Start polling for messages
bot.polling(none_stop=True)