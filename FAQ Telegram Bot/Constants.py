# Files and Paths
DataDirectory = "FAQ Telegram Bot/Data/"
FAQScriptName = "FAQ.script"

# Settings (To be moved to Settings.json eventually)
MaxLoginAttempts = 3

# FileIO characters
ScriptLevel = "-"
NewLine = "\n"
TabSpacing = "\t"
IdentifierKey_QandA = "Answer"
IdentifierKey_Category = "Message"

# Media definitions
ImgExtensions = [".jpg", "jpeg", ".png"]
VidExtensions = [".mp3", ".mp4"]

# Media Type Constants
MEDIA_NONE = 0
MEDIA_IMAGE = 1
MEDIA_VIDEO = 2

# User Role Constants
ROLE_DEFAULT = 0
ROLE_ADMIN = 1
ROLE_LOCKED = 2 # Locked role will not be able to login

# App State Constants
APPSTATE_FAQ = 0
APPSTATE_QUESTIONS = 1
APPSTATE_QUESTIONS_EDIT = 1.3
APPSTATE_FEEDBACK = 2

# Universal Callback
CALLBACK_BACK = "Back"
CALLBACK_EXIT = "Exit"

# Modify Questions Callback 
CALLBACK_QUESTIONS_CREATE_QNA = "Question_Create_QNA"
CALLBACK_QUESTIONS_CREATE_CATEGORY = "Question_Create_Category"
CALLBACK_QUESTIONS_EDIT = "Question_Edit"
CALLBACK_QUESTIONS_EDIT_Q = "Question_Edit_Q"
CALLBACK_QUESTIONS_EDIT_A = "Question_Edit_A"

# Feedback Callback
CALLBACK_FEEDBACK_REPLY = "Reply"

# Create Question Temp Data Keys
KEY_CREATE_QUESTION_Q = "Create_Question_Q" # Question key
KEY_CREATE_QUESTION_A = "Create_Question_A" # Answer key
KEY_CREATE_QUESTION_C = "Create_Question_C" # Callback key

# Edit Question Temp Data Keys
KEY_EDIT_QUESTION_ACTION = "Edit_Question_Action"
KEY_EDIT_QUESTION_Q = "Edit_Question_Q"
KEY_EDIT_QUESTION_A = "Edit_Question_A"

# Feedback Temp Data Keys
KEY_FEEDBACK_REPLY_ID = "Feedback_Reply_ID"
KEY_FEEDBACK_REPLY_INDEX = "Feedback_Reply_Index"
KEY_FEEDBACK_REPLY_REPLY = "Feedback_Reply_Reply"