# Python libs import
import json

# Telebot imports
from telebot import TeleBot
from telebot.types import InputMediaPhoto, InputMediaVideo, InlineKeyboardMarkup, InlineKeyboardButton

# Class imports
from QandA import QandA
from Category import Category
from BotUser import BotUser

# Constant imports
from Constants import DataDirectory, FAQScriptName
from Constants import ROLE_ADMIN, ROLE_LOCKED
from Constants import CALLBACK_QUESTIONS_CREATE_QNA, CALLBACK_QUESTIONS_CREATE_CATEGORY, CALLBACK_QUESTIONS_EDIT
from Constants import APPSTATE_FAQ, APPSTATE_QUESTIONS, APPSTATE_QUESTIONS_CREATE_CATEGORY, APPSTATE_QUESTIONS_CREATE_QNA
from Constants import KEY_CREATE_QUESTION_Q, KEY_CREATE_QUESTION_A, KEY_CREATE_QUESTION_C

# Method imports
from FileIO import LoadScript, SaveScript


### Script and state data ###
UserStates = {}
FAQScript = Category("Main", "What would you like to know?", True)

### Load credentials ###
credentialsFile = open(DataDirectory + "Credentials.json", "r")
credentials = json.load(credentialsFile)
credentialsFile.close()

# Create bot
bot = TeleBot(credentials["token"])

### Helper Functions ###

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


def FetchUser(id) -> BotUser:
    if id not in UserStates:
        UserStates[id] = BotUser(id)
    return UserStates[id]


def TraverseFAQScript(script : Category, state, current = 0) -> Category:
    if current >= len(state):
        return script
    else:
        return TraverseFAQScript(script.ActionList[state[current]], state, current + 1)

### End of Helper Functions ###


### Generic Command handling ###

@bot.message_handler(commands=["start"])
def Start_Command(m):
    ### Send main message ###
    # Retrieve message and markup
    message, markup, newState = FAQScript.Selected(None, [])
    
    # Reset user state
    FetchUser(m.chat.id).ResetFAQState()

    # Send message
    SendMessage(m.chat.id, message, markup)


@bot.message_handler(commands=["help"])
def Help_Command(m):
    # Send media
    SendMessage(m.chat.id, "/start\n/media")

### End of Generic Command handling ###


### Callback Query handling ###

@bot.callback_query_handler(lambda query : query.data != "")
def Callback(query):
    # Fetch user id
    user = FetchUser(query.message.chat.id)

    if user.AppState == APPSTATE_FAQ:
        # Fetch message and markup
        message, markup, newState = FAQScript.Selected(query.data, user.FAQState)

        # Update new state
        user.FAQState = newState

        # Send message
        SendMessage(query.message.chat.id, message, markup)
    elif user.AppState == APPSTATE_QUESTIONS:
        if query.data == CALLBACK_QUESTIONS_CREATE_QNA:
            # Creating new question
            user.AppState = APPSTATE_QUESTIONS_CREATE_QNA
            SendMessage(user.ID, "Please write the question to ask")
            bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_QNA_Q)
        elif query.data == CALLBACK_QUESTIONS_CREATE_CATEGORY:
            # Create new category
            user.AppState = APPSTATE_QUESTIONS_CREATE_CATEGORY
            SendMessage(user.ID, "Please write the name of the Category")
            bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_Category)
            pass
        elif query.data == CALLBACK_QUESTIONS_EDIT:
            # Edit action from current category
            pass


### End of CallBack Query handling ###


### Create Q&A Next Step Handlers ###

def Create_Question_QNA_Q(m):
    user = FetchUser(m.chat.id)

    # Register question into user temp data
    user.TempData[KEY_CREATE_QUESTION_Q] = m.text

    # Prompt for answer input
    SendMessage(user.ID, "Please write the answer to question")

    # Register next step to answer
    bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_QNA_A)


def Create_Question_QNA_A(m):
    user = FetchUser(m.chat.id)
    
    # Register answer into user temp data
    user.TempData[KEY_CREATE_QUESTION_A] = m.text

    # Prompt for confirmation
    SendMessage(user.ID, "Please confirm the question(Y/N)\nQ: " + user.TempData[KEY_CREATE_QUESTION_Q] + "\nA: " + m.text)

    # Register next step to answer
    bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_QNA_Confirm)


def Create_Question_QNA_Confirm(m):
    user = FetchUser(m.chat.id)
    if m.text == "Y" or m.text == "y":
        # Add question into category
        TraverseFAQScript(FAQScript, user.FAQState).AddAction(QandA(user.TempData[KEY_CREATE_QUESTION_Q], user.TempData[KEY_CREATE_QUESTION_A], None))

        # Save script
        SaveScript(DataDirectory + "Save.script", FAQScript)

        # Delete temp data
        del user.TempData[KEY_CREATE_QUESTION_Q]
        del user.TempData[KEY_CREATE_QUESTION_A]

        # Send added message
        SendMessage(user.ID, "Question added successfully")

        # Update app state back to FAQ
        user.AppState = APPSTATE_FAQ
    elif m.text == "N" or m.text == "n":
        # Send cancel message
        SendMessage(user.ID, "Question was not added")

        # Delete temp data
        del user.TempData[KEY_CREATE_QUESTION_Q]
        del user.TempData[KEY_CREATE_QUESTION_A]

        # Update app state back to FAQ
        user.AppState = APPSTATE_FAQ
    else:
        # Wrong input
        SendMessage(user.ID, "Invalid Confirmation, please enter \"Y\" or \"N\"")
        bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_QNA_Confirm)

### End of Create Q&A Next Step Handlers ###


### Create Category Next Step Handlers ###

def Create_Question_Category(m):
    user = FetchUser(m.chat.id)
    
    # Register answer into user temp data
    user.TempData[KEY_CREATE_QUESTION_C] = m.text

    # Prompt for confirmation
    SendMessage(user.ID, "Please confirm the Category(Y/N)\nName: " + m.text)

    # Register next step to answer
    bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_Category_Confirmation)

def Create_Question_Category_Confirmation(m):
    user = FetchUser(m.chat.id)
    if m.text == "Y" or m.text == "y":
        # Add question into category
        TraverseFAQScript(FAQScript, user.FAQState).AddAction(Category(user.TempData[KEY_CREATE_QUESTION_C], None))

        # Save script
        SaveScript(DataDirectory + "Save.script", FAQScript)

        # Delete temp data
        del user.TempData[KEY_CREATE_QUESTION_C]

        # Send added message
        SendMessage(user.ID, "Category added successfully")

        # Update app state back to FAQ
        user.AppState = APPSTATE_FAQ
    elif m.text == "N" or m.text == "n":
        # Send cancel message
        SendMessage(user.ID, "Category was not added")

        # Delete temp data
        del user.TempData[KEY_CREATE_QUESTION_C]

        # Update app state back to FAQ
        user.AppState = APPSTATE_FAQ
    else:
        # Wrong input
        SendMessage(user.ID, "Invalid Confirmation, please enter \"Y\" or \"N\"")
        bot.register_next_step_handler_by_chat_id(user.ID, Create_Question_Category_Confirmation)

### End of Create Category Next Step Handlers ###


### Admin Functions ###

@bot.message_handler(commands=["login"])
def Login_Command(m):
    # Fetch user
    user = FetchUser(m.chat.id)

    # Check user is locked
    if user.Role == ROLE_LOCKED:
        SendMessage(user.ID, "Unable to login")
    else:
        # Check user is admin
        if user.Role != ROLE_ADMIN:
            # Split command message to get password
            split = m.text.split(" ")
            if len(split) > 1 and split[1] == credentials["password"]:
                # Update user role to admin upon login
                user.Role = ROLE_ADMIN
                SendMessage(user.ID, "Login successful")
            else:
                # Incorrect password entered
                user.AttemptLoginFail()
                SendMessage(user.ID, "Incorrect password entered, try again.")
        else:
            SendMessage(user.ID, "You are already logged in.")
            
    # Delete login command message for security
    bot.delete_message(user.ID, m.message_id)


@bot.message_handler(commands=["questions"])
def Questions_Command(m):
    user = FetchUser(m.chat.id)
    if user.Role != ROLE_ADMIN:
        SendMessage(user.ID, "Insufficient permission, please login to proceed")
        return

    # Update app state
    user.AppState = APPSTATE_QUESTIONS

    # Create markup
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Add a Question to current Category", callback_data=CALLBACK_QUESTIONS_CREATE_QNA)
    ).add(
        InlineKeyboardButton("Add a Category to current Category", callback_data=CALLBACK_QUESTIONS_CREATE_CATEGORY)
    ).add(
        InlineKeyboardButton("Edit current questions in Category", callback_data=CALLBACK_QUESTIONS_EDIT)
    )
    SendMessage(user.ID, "What would you like to do with the questions?", reply_markup=markup)


@bot.message_handler(commands=["cancel"])
def Cancel_Command(m):
    SendMessage(m.chat.id, "Cancel command called called")

### End of Admin Functions ###

# Capture all text messages that are not commands
@bot.message_handler(func=lambda m : not m.text.startswith("/"), content_types=["text"])
def AnyTextMessage(m):
    SendMessage(m.chat.id, "Type /start to begin or /help to find possible commands.")


### Bot execution starts here
# Load FAQ script
LoadScript(DataDirectory + FAQScriptName, FAQScript)
    
# Start polling for messages
bot.polling(none_stop=True)
