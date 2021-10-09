from Action import Action
from Constants import ImgExtensions, VidExtensions, MEDIA_NONE, MEDIA_IMAGE, MEDIA_VIDEO, DataDirectory, ScriptLevel, NewLine, TabSpacing
from telebot.types import InputMediaPhoto, InputMediaVideo

class QandA(Action):
    def __init__(self, question : str, answer : str, media : str) -> None:
        super().__init__(question)

        self.Answer = answer

        # Media
        self.Media = media
        self.MediaType = self.IdentifyMedia(media)


    def DisplayMessage(self):
        if self.MediaType == MEDIA_NONE:
            return self.Answer
        else:
            media = open(DataDirectory + self.Media, "rb")
            if self.MediaType == MEDIA_IMAGE:
                return InputMediaPhoto(media, self.Answer)
            elif self.MediaType == MEDIA_VIDEO:
                return InputMediaVideo(media, self.Answer)


    # Render the feedback when selected
    def Selected(self, callback : str, state):
        return self.DisplayMessage()

    
    def ToString(self, level) -> str:
        # Level
        result = (ScriptLevel * level) + NewLine

        # Open curly braces
        oneLessTabSpace = TabSpacing * (level - 1)
        result += oneLessTabSpace + "{" + NewLine

        # Question
        tabSpace = TabSpacing * level
        result += tabSpace + "\"Question\" : \"" + self.Name + "\"," + NewLine

        # Answer
        result += tabSpace + "\"Answer\" : \"" + self.Answer + "\""

        # Media
        if self.MediaType != MEDIA_NONE:
            # Add comma and new line
            result += ("," + NewLine)
            result += tabSpace + "\"Media\" : \"" + self.Media + "\""
        result += NewLine

        # Close curly braces
        result += oneLessTabSpace + "}" + NewLine

        return result


    def IdentifyMedia(self, media : str) -> int:
        # Check if media is specified
        if not media or len(media) <= 0:
            return MEDIA_NONE

        # Get media ext
        split = media.split(".")
        if len(split) > 1:
            ext = "." + split[len(split) - 1]

            # Check if media is image
            if ext in ImgExtensions:
                return MEDIA_IMAGE

            if ext in VidExtensions:
                return MEDIA_VIDEO

        # No media type found
        return MEDIA_NONE