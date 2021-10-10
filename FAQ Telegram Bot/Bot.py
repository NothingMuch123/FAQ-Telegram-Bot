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
from Constants import ROLE_DEFAULT, ROLE_ADMIN, ROLE_LOCKED
from Constants import CALLBACK_QUESTIONS_CREATE_QNA, CALLBACK_QUESTIONS_CREATE_CATEGORY, CALLBACK_QUESTIONS_EDIT, CALLBACK_FEEDBACK_EXIT, CALLBACK_FEEDBACK_REPLY
from Constants import APPSTATE_FAQ, APPSTATE_QUESTIONS, APPSTATE_QUESTIONS_CREATE_CATEGORY, APPSTATE_QUESTIONS_CREATE_QNA, APPSTATE_FEEDBACK
from Constants import KEY_CREATE_QUESTION_Q, KEY_CREATE_QUESTION_A, KEY_CREATE_QUESTION_C, KEY_FEEDBACK_REPLY_ID, KEY_FEEDBACK_REPLY_INDEX, KEY_FEEDBACK_REPLY_REPLY

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
    user = FetchUser(m.chat.id)
    user.AppState = APPSTATE_FAQ
    user.ResetFAQState()

    # Send message
    SendMessage(m.chat.id, message, markup)


@bot.message_handler(commands=["help"])
def Help_Command(m):
    # Send media
    SendMessage(m.chat.id, "/start\n/media")


@bot.message_handler(commands=["feedback"])
def Feedback_Command(m):
    user = FetchUser(m.chat.id)
    if user.Role == ROLE_ADMIN:
        # Update user state to feedback
        user.AppState = APPSTATE_FEEDBACK

        # View feedbacks
        markup = InlineKeyboardMarkup()
        # Run through all registered users
        for u in UserStates.values():
            # Ensure that you do not answer your own feedback
            #if u != user:
            u.AddFeedbacksIntoMarkup(markup)
        # Add exit button
        markup.add(InlineKeyboardButton("Exit feedback", callback_data=CALLBACK_FEEDBACK_EXIT))
        SendMessage(user.ID, "Which feedback do you like to view?", reply_markup=markup)
    else:
        # Write feedback
        split = m.text.split(" ")
        if len(split) < 2:
            SendMessage(user.ID, "No feedback found, please try again")
        else:
            user.WriteFeedback(" ".join(split[1:]))
            SendMessage(user.ID, "Feedback recorded, we will get back to your shortly")
        pass

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
        elif query.data == CALLBACK_QUESTIONS_EDIT:
            # Edit action from current category
            pass
    elif user.AppState == APPSTATE_FEEDBACK:
        # Admin feedback state
        if query.data == CALLBACK_FEEDBACK_EXIT:
            # Exiting feedback state
            user.AppState = APPSTATE_FAQ
        else:
            split = query.data.split(BotUser.FEEDBACK_SPLIT)
            if len(split) >= 2:
                feedbackUser = FetchUser(int(split[0]))
                feedback = feedbackUser.RetrieveFeedback(split[1])
                if feedback:
                    if query.data.endswith(CALLBACK_FEEDBACK_REPLY):
                        # Write feedback details into temp data
                        user.TempData[KEY_FEEDBACK_REPLY_ID] = feedbackUser.ID
                        user.TempData[KEY_FEEDBACK_REPLY_INDEX] = split[1]
                        # Replying to feedback
                        SendMessage(user.ID, "Please enter the feedback's reply")
                        bot.register_next_step_handler_by_chat_id(user.ID, Reply_Feedback)
                    else:
                        # Sending feedback with reply button
                        SendMessage(user.ID, "User " + str(feedbackUser.ID) + " feedbacks:\n" + feedback,
                        reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Reply to feedback", callback_data=query.data + BotUser.FEEDBACK_SPLIT + CALLBACK_FEEDBACK_REPLY)).add(
                            InlineKeyboardButton("Exit feedback", callback_data=CALLBACK_FEEDBACK_EXIT)))
                else:
                    SendMessage(user.ID, "Could not find feedback from " + feedbackUser.ID)
                    Feedback_Command(query.message)


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


### Reply Feedback Next Step Handlers ###

def Reply_Feedback(m):
    user = FetchUser(m.chat.id)

    # Store in temp data
    user.TempData[KEY_FEEDBACK_REPLY_REPLY] = m.text

    # Prompt for confirmation
    SendMessage(user.ID, "Please confirm the Feedback reply(Y/N)\nReply: " + m.text)
    bot.register_next_step_handler_by_chat_id(user.ID, Reply_Feedback_Confirm)


def Reply_Feedback_Confirm(m):
    user = FetchUser(m.chat.id)
    if m.text == "Y" or m.text == "y":
        # Send feedback reply to feedback user
        feedbackUser = FetchUser(user.TempData[KEY_FEEDBACK_REPLY_ID])
        feedback = feedbackUser.RetrieveFeedback(user.TempData[KEY_FEEDBACK_REPLY_INDEX])
        if feedback:
            # Send reply to feedback user
            SendMessage(feedbackUser.ID, "Feedback:\n" + feedback + "\n\n" + "Reply:\n" + user.TempData[KEY_FEEDBACK_REPLY_REPLY])

            # Update admin that feedback replied
            SendMessage(user.ID, "Feedback replied successfully")

            # Delete feedback
            feedbackUser.RemoveFeedback(user.TempData[KEY_FEEDBACK_REPLY_INDEX])

        else:
            SendMessage(user.ID, "No feedback found, no reply sent")

        # Delete temp data
        del user.TempData[KEY_FEEDBACK_REPLY_ID]
        del user.TempData[KEY_FEEDBACK_REPLY_INDEX]
        del user.TempData[KEY_FEEDBACK_REPLY_REPLY]

        # Update app state back to Feedback
        user.AppState = APPSTATE_FEEDBACK
        Feedback_Command(m)
    elif m.text == "N" or m.text == "n":
        # Send cancel message
        SendMessage(user.ID, "Feedback reply was not sent")

        # Delete temp data
        del user.TempData[KEY_FEEDBACK_REPLY_ID]
        del user.TempData[KEY_FEEDBACK_REPLY_INDEX]
        del user.TempData[KEY_FEEDBACK_REPLY_REPLY]

        # Update app state back to Feedback
        user.AppState = APPSTATE_FEEDBACK
        Feedback_Command(m)
    else:
        # Wrong input
        SendMessage(user.ID, "Invalid Confirmation, please enter \"Y\" or \"N\"")
        bot.register_next_step_handler_by_chat_id(user.ID, Reply_Feedback_Confirm)

### End of Reply Feedback Next Step Handlers ###


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


@bot.message_handler(commands=["logout"])
def Logout_Command(m):
    # Fetch user
    user = FetchUser(m.chat.id)
    
    if user.Role == ROLE_ADMIN:
        user.Role = ROLE_DEFAULT
        SendMessage(user.ID, "Logout successfully")
    else:
        SendMessage(user.ID, "Not logged in")


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
