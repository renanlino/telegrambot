import requests
from datetime import datetime
from .types import (Update, User, Chat, Message, PhotoSize,
                    Audio, Document, Sticker, Video, Contact,
                    Location, InputFile, UserProfilePhotos)
from ._aux import *
import json
import logging
import ast

GLOBAL_TIMEOUT = 10
#requests.packages.urllib3.disable_warnings()

class Bot:
    """
    Bot class based by Telegram API at https://core.telegram.org/bots/api
    This is the main class of API. All methods available from Bot API
    (https://core.telegram.org/bots/api#available-methods) are methods
    of this class.
    Some additional methods are provided too.

        Attribute        Type        Description
        token            string      token provided by Botfather for your bot
        apiURL           string      base URL for API access
        messages         [Message]   array with messages sent for this bot
        success          bool        check if the boy was successfully started
        me               User        information about this bot
        vars             dict        general purpose dictionary, available to you set any internal variable
        offset           int         (ID + 1) of last received message from server. to avoid duplicates.
        auto_status      bool        set True for auto send chat status while uploading objects
    """
    def __init__(self, token, offset=0, auto_status=False):
        """
        (str, int, bool) -> constructor
        Bot class constructor. Initializes a bot object with provided token.
        """

        #token provided by Botfather for your bot
        self.token = token
        #base URL for API access
        self.apiURL = "https://api.telegram.org/bot" + self.token + "/"
        #information about this bot
        self.me = None
        if self.getMe() is None:
            logging.warning("Bot.__init__(): Failed to start a bot. Aborting.")
            #check if the boy was successfully started
            self.success = False
        else:
            logging.info("Bot.__init__(): Bot %s started.", self.me.first_name)
            self.success = True
            #array with messages sent for this bot
            self.messages = []
            #general purpose dictionary
            self.vars = {}
            #(ID + 1) of last received message from server. to avoid duplicates.
            self.offset = offset
            #set True for auto send chat status while uploading objects
            self.auto_status = auto_status

    def getMe(self):
        """
        () -> None/True
        Get bot information from server
        https://core.telegram.org/bots/api#getme
        """
        try:
            logging.info("Bot.getMe(): Requesting information.")
            myData = requests.get(self.apiURL + "getMe", timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
            return None

        if not myData["ok"]:
            logging.warning("Bot.getMe(): Error while trying to get bot information. Aborting.")
            logging.info("          Server's answer:\n          Error %d: %s" %( myData["error_code"], myData["description"] ))
            return None
        else:
            myData = myData["result"]

        self.me = User(myData)
        return True

    def getUpdates(self):
        """
        () -> None/True
        Get messages from server using the getUpdates API method.
        https://core.telegram.org/bots/api#getupdates
        """
        parameters = {"offset":self.offset}

        try:
            logging.info("Bot.getUpdates(): Requesting updates.")
            updatesJSON = requests.get(self.apiURL + "getUpdates", params=parameters, timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
            logging.warning("Bot.getUpdates(): requests raises an exception. Aborting.")
            return None

        if not updatesJSON["ok"]:
            logging.warning("Bot.getUpdates(): Server returned an error.")
            logging.info("          Server's answer:\n          Error %d: %s" %( updatesJSON["error_code"], updatesJSON["description"] ))
            return None
        updatesJSON = updatesJSON["result"]
        logging.info("Bot.getUpdates(): There is %d new messages in this update" %len(updatesJSON))
        for update in updatesJSON:
            if "message" in update:
                update = Update(update)
                self.messages.append(update.message)
                if update.update_id >= self.offset -1:
                    self.offset = update.update_id + 1
        logging.info("Bot.getUpdates(): Success.")
        return True


    def sendMessage(self, to, text, disable_web_page_preview=False, replyTo=None, reply_markup=None):
        """
        (User/Chat, string, bool, Message, not supported yet) -> None/Message
        Send a text message. Return the sent message on success.
        https://core.telegram.org/bots/api#sendmessage
        """

        parameters = {"chat_id":to.id, "text":text, "disable_web_page_preview":disable_web_page_preview}
        if replyTo != None:
            parameters["reply_to_message_id"] = replyTo.id
        if reply_markup != None:
            parameters["reply_markup"] = reply_markup.toJSON()

        try:
            logging.info("Bot.sendMessage(): Sending a message.")
            messagePingback = requests.get(self.apiURL + "sendMessage", params=parameters, timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
            logging.warning("Bot.sendMessage(): requests raises an exception. Aborting.")
            return None

        if not messagePingback["ok"]:
            logging.warning("Bot.sendMessage(): Failed to send.")
            logging.info("          Server's answer:\n          Error %d: %s" %( messagePingback["error_code"], messagePingback["description"] ))
            return None

        logging.info("Bot.sendMessage(): Success.")
        return Message( messagePingback["result"] )

    def forwardMessage(self, to, message):
        """
        (User/Chat, Message) -> None/Message
        Forward any message. Return the sent message on success.
        https://core.telegram.org/bots/api#forwardmessage
        """

        parameters = {"chat_id":to.id, "from_chat_id":message.chat.id, "message_id":message.message_id}

        try:
            logging.info("Bot.forwardMessage(): Forwarding a message.")
            ans = requests.get(self.apiURL + "forwardMessage", params = parameters, timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
            logging.warning("Bot.forwardMessage(): requests raises an exception. Aborting.")
            return None

        if not ans["ok"]:
            logging.warning("Bot.forwardMessage(): Failed to send.")
            logging.info("          Server's answer:\n          Error %d: %s" %( ans["error_code"], ans["description"] ))
            return None
        logging.info("Bot.forwardMessage(): Success.")
        return Message( ans["result"] )


    def sendObject(self, to, inputObj=None, obj=None, objType=None, caption=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, any object type, string, string, Message, not supported yet) -> Message
        'any object type' should be PhotoSize, Audio, Document, Sticker, Video, Contact or Location object.
        Return the sent message on success.
        """

        parameters = {"chat_id":to.id, "caption":caption, "reply_to_message_id":replyTo}
        if replyTo != None:
            parameters["reply_to_message_id"] = replyTo.message_id
        if reply_markup != None:
            parameters["reply_markup"] = reply_markup.toJSON()

        if (inputObj == None and obj == None) or objType == None:
            logging.warning("Bot.sendObject(): Bad request. Bot arguments are None or no type specified. Aborting.")
            return None

        elif obj == None and objType != None:
            files = {objType:inputObj.file}
            if files[objType] is None:
                logging.warning("Bot.sendObject(): Bad file to upload. Aborting.")
                return None

            try:
                logging.info("Bot.sendObject(): Uploading file of type %s" %objType)
                ans = requests.post(self.apiURL + "send" + objType.title(), files = files,
                                    params = parameters, timeout=GLOBAL_TIMEOUT).json()
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
                logging.warning("Bot.sendObject(): requests raises an exception. Aborting.")
                return None



        elif inputObj == None and objType != None:
            parameters[objType] = obj.file_id
            try:
                logging.info("Bot.sendObject(): Resending file of type %s" %objType)
                ans = requests.post(self.apiURL + "send" + objType.title(),
                                    params = parameters, timeout=GLOBAL_TIMEOUT).json()
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
                logging.warning("Bot.sendObject(): requests raises an exception. Aborting.")
                return None

        else:
            logging.warning("Bot.sendObject(): Bad request. Aborting")
            return None

        if not ans["ok"]:
            logging.warning("Bot.sendObject(): Failed to send.")
            logging.info("          Server's answer:\n          Error %d: %s" %( ans["error_code"], ans["description"] ))
            return None
        ans = Message( ans["result"] )
        return ans

    def sendPhoto(self, to, inputObj=None, obj=None, caption=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, PhotoSize, string, Message, not supported yet) -> Message
        Send a photos. Use 'inputObj' to upload a photo OR 'obj' to send an already uploaded photo.
        Do not set both arguments!
        Return the sent message on success.
        https://core.telegram.org/bots/api#sendphoto
        """
        if self.auto_status:
            self.sendChatAction(to, "upload_photo")
        return self.sendObject(to, inputObj=inputObj, obj=obj, objType="photo", caption=caption, replyTo=replyTo, reply_markup=reply_markup)

    def sendAudio(self, to, inputObj=None, obj=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, Audio, Message, not supported yet) -> Message
        Send an audio (voice notes). Use 'inputObj' to upload an audio file OR 'obj' to send
        an already uploaded audio.
        Do not set both arguments!
        Return the sent message on success.
        https://core.telegram.org/bots/api#sendaudio
        """
        if self.auto_status:
            self.sendChatAction(to, "upload_audio")
        return self.sendObject(to, inputObj=inputObj, obj=obj, objType="audio", replyTo=replyTo, reply_markup=reply_markup)


    def sendVoice(self, to, inputObj=None, obj=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, Audio, Message, not supported yet) -> Message
        Send an voice (voice notes). Use 'inputObj' to upload an audio file OR 'obj' to send
        an already uploaded audio.
        Do not set both arguments!
        Return the sent message on success.
        https://core.telegram.org/bots/api#sendaudio
        """
        if self.auto_status:
            self.sendChatAction(to, "upload_audio")
        return self.sendObject(to, inputObj=inputObj, obj=obj, objType="voice", replyTo=replyTo, reply_markup=reply_markup)

    def sendDocument(self, to, inputObj=None, obj=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, Document, Message, not supported yet) -> Message
        Send a document (generic file). Use 'inputObj' to upload a file OR 'obj' to send
        an already uploaded file.
        Do not set both arguments!
        Return the sent message on success.
        https://core.telegram.org/bots/api#senddocument
        """
        if self.auto_status:
            self.sendChatAction(to, "upload_document")
        return self.sendObject(to, inputObj=inputObj, obj=obj, objType="document", replyTo=replyTo, reply_markup=reply_markup)

    def sendSticker(self, to, inputObj=None, obj=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, Sticker, Message, not supported yet) -> Message
        Send a sticker. Use 'inputObj' to upload a stciker file OR 'obj' to send
        an already uploaded sticker.
        Do not set both arguments!
        Return the sent message on success.
        https://core.telegram.org/bots/api#sendsticker
        """
        return self.sendObject(to, inputObj=inputObj, obj=obj, objType="sticker", replyTo=replyTo, reply_markup=reply_markup)

    def sendVideo(self, to, inputObj=None, obj=None, replyTo=None, reply_markup=None):
        """
        (User/Chat, InputFile, Video, string, Message, not supported yet) -> Message
        Send a video. Use 'inputObj' to upload an video file OR 'obj' to send
        an already uploaded audio.
        Do not set both arguments!
        Return the sent message on success.
        https://core.telegram.org/bots/api#sendvideo
        """
        if self.auto_status:
            self.sendChatAction(to, "upload_video")
        return self.sendObject(to, inputObj=inputObj, obj=obj, objType="video", replyTo=replyTo, reply_markup=reply_markup)

    def sendLocation(self, to, obj, replyTo=None, reply_markup=None):
        """
        (User/Chat, Location, Message, not supported yet) -> Message
        Send a location.
        Return the sent message on success.
        https://core.telegram.org/bots/api#sendlocation
        """
        if self.auto_status:
            self.sendChatAction(to, "find_location")

        parameters = {"chat_id":to.id, "latitude":obj.latitude,
                      "longitude":obj.longitude, "objType":"location"}
        if replyTo != None:
            parameters["reply_to_message_id"] = replyTo.message_id
        if reply_markup != None:
            parameters["reply_markup"] = reply_markup.toJSON()

        try:
            ans = requests.get(self.apiURL + "sendLocation", params = parameters, timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
                return None
        if not ans["ok"]:
            return None
        ans = Message( ans["result"] )
        return ans


    def sendChatAction(self, to, action):
        """
        (User/Chat, string) -> None/True
        Set a chat action. 'action' should be one of the following options:
        "typing", "upload_photo", "record_video", "upload_video",
        "record_audio", "upload_audio", "upload_document" or "find_location"
        """
        if action not in ["typing", "upload_photo", "record_video", "upload_video",
                          "record_audio", "upload_audio", "upload_document", "find_location"]:
            return None
        parameters = {"chat_id":to.id, "action":action}
        try:
            ans = requests.get(self.apiURL + "sendChatAction", params = parameters, timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
                return None
        if not ans["ok"]:
            return None
        else:
            return True

    def getFile(self, file_obj):
        """
        (Video/Document/Audio/PhotoSize/Voice) -> File
        Request a download link.
        Returns a File object.
        """
        parameters = {"file_id":file_obj.file_id}
        try:
            ans = requests.get(self.apiURL + "getFile", params = parameters, timeout=GLOBAL_TIMEOUT).json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
                return None
        if not ans["ok"]:
            return None
        else:
            return File ( ans["result"] )

    def downloadFile(self, file_obj, dest_path):
        """
        (File) -> bool
        """
        logging.info("Bot.downloadFile(): Starting download request.")
        if file_obj.file_path == None:
            return None
        try:
            ans = requests.get("https://api.telegram.org/file/bot" + self.token + "/" + file_obj.file_path, stream=True, timeout=GLOBAL_TIMEOUT)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects):
                return None
        try:
            with open(dest_path, "wb") as f:
                for chunk in ans.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        except IOError:
            return None
        return True


    def flushMessages(self):
        """
        () -> None
        Delete all messages from bot array.
        """
        logging.info("Bot.flushMessages(): Flushing messages.")
        self.messages = []

    def ping(self, message):
        """
        (Message) -> None
        Sends the sent message to sender. Useful for tests.
        """
        """
        if message.type == "photo":
            self.sendPhoto(message.chat, obj=message.content[0])
        elif message.type == "text":
            self.sendMessage(message.chat, text=message.content)
        elif message.type == "document":
            self.sendDocument(message.chat, obj=message.content)
        elif message.type == "video":
            self.sendVideo(message.chat, obj=message.content)
        elif message.type == "audio":
            self.sendAudio(message.chat, obj=message.content)
        elif message.type == "location":
            self.sendLocation(message.chat, obj=message.content)
        elif message.type == "sticker":
            self.sendSticker(message.chat, obj=message.content)
        elif message.type == "location":
            self.sendLocation(message.chat, obj=message.content)
        elif message.type == "contact":
            self.sendMessage(message.chat, text=str(message.content))
        else:
            self.sendMessage(message.chat, text="Data type not supported yet")
        """
        logging.info("Bot.ping(): Forwarding message back to sender.")
        self.forwardMessage(message.chat, message)

    def __repr__(self):
        """
        () -> str
        Formal representantion for Bot object (a valid dictionary representation)
        Useful for dump bot content to a persistent file
        """
        logging.info("Bot.__repr__(): Call for repr() to bot.")
        return str(self.__dict__)

    def __str__(self):
        """
        () -> str
        Human readable representation for Bot object
        """
        string = ( "Hello. I'am %s, a Telegram Bot under your command.\n" %(self.me.first_name) )
        string += ("My Telegram link is telegram.me/%s." %(self.me.username))
        return string

    def dumpMeTo(self, filepath):
        logging.info("Bot.dumpMeTo(): Dumping bot information to %s" %filepath)
        dumpFile = openFile(filepath, "w")
        if dumpFile is None:
            logging.info("Bot.dumpMeTo(): File error. Aborting.")
            return None
        json.dump( ast.literal_eval( repr(self) ), dumpFile, indent=3 )
        dumpFile.close()
        return True
