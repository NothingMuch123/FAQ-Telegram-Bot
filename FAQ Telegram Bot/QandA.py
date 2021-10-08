from Action import Action
from Constants import ImgExtensions, VidExtensions, MEDIA_NONE, MEDIA_IMAGE, MEDIA_VIDEO, DataDirectory
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
    def Selected(self, callback):
        return self.DisplayMessage()

    
    def ToString(self, level) -> str:
        pass


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